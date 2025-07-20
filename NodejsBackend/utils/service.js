import dotenv from "dotenv";
dotenv.config();

import { ChatGroq } from "@langchain/groq";
import { HuggingFaceInferenceEmbeddings } from "@langchain/community/embeddings/hf";
import { PineconeStore } from "@langchain/pinecone";
import { Pinecone } from "@pinecone-database/pinecone";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import { createRetrievalChain } from "langchain/chains/retrieval";
import { createHistoryAwareRetriever } from "langchain/chains/history_aware_retriever";
import { HumanMessage, AIMessage } from "@langchain/core/messages";

const PINECONE_API_KEY = process.env.PINECONE_API_KEY;
const PINECONE_INDEX_NAME = process.env.PINECONE_INDEX_NAME;
const GROQ_API_KEY = process.env.GROQ_API_KEY;
const HF_TOKEN = process.env.HF_TOKEN;


let conversationalRetrievalChain;

export async function initializeLangchain() {
    if (conversationalRetrievalChain) return;

    const pinecone = new Pinecone({ apiKey: PINECONE_API_KEY });
    const pineconeIndex = pinecone.index(PINECONE_INDEX_NAME);

    const embeddings = new HuggingFaceInferenceEmbeddings({
        apiKey: HF_TOKEN,
        model: "sentence-transformers/all-mpnet-base-v2",
    });

    const vectorstore = new PineconeStore(embeddings, { pineconeIndex });
    const llm = new ChatGroq({ model: "llama3-8b-8192", apiKey: GROQ_API_KEY });

    const retriever = vectorstore.asRetriever({
        searchType: "similarity_score_threshold",
        searchKwargs: { k: 5, scoreThreshold: 0.5 },
    });

    const historyAwarePrompt = ChatPromptTemplate.fromMessages([
        new MessagesPlaceholder("chat_history"),
        ["user", "{input}"],
        ["user", "Given the above conversation, formulate a standalone question that can be understood without the chat history. Do not answer the question, just reformulate it if needed and otherwise return it as is. Return only the question."],
    ]);

    const historyAwareRetrieverChain = await createHistoryAwareRetriever({
        llm,
        retriever,
        rephrasePrompt: historyAwarePrompt,
    });

    const qaSystemPrompt = `You are an intelligent legal assistant who is specialised in answering user queries about commercial cases and laws.
Use the given context and chat history to answer the user's question to the best of your capacity.
Keep the answer to about 2 paragraphs maximum and no need to mention according to context in the answer.
Don't answer outside the domain of commercial cases and law.
No need to mention that you are using any context for every answer. Just converse normally.
<context>
{context}
</context>
Question: {input}

Instructions for answering:
1. If the provided context directly and specifically answers the user's question, use the information from the context to formulate your answer.
2. If the context is related to the general topic or entities mentioned in the question but does NOT contain a specific answer to the user's precise query (e.g., user asks for 'Specific Case X vs Y' and context contains general information about companies X and Y but not that particular case), you MUST state that you do not have information on that specific query within the provided documents. You may then, if you deem it helpful, provide some general, relevant information about the entities or topic based on your own knowledge, but clearly distinguish this from the information (or lack thereof) in the context.
3. If the context is completely irrelevant to the question or if it's empty, clearly state that you cannot answer the question based on the provided documents.
4. Only attribute sources (implicitly, by using the context) if your answer directly uses information from those context documents. If you are stating you don't have specific information from the documents or are using general knowledge, the provided context documents are not the source for that part of your statement.
5. Keep your answer concise, ideally to about 2 paragraphs maximum.
6. Do not explicitly mention "according to the context" or "based on the documents" in your response; just answer naturally.
7. Do not answer questions outside the domain of commercial cases and law.`;

    const qaPrompt = ChatPromptTemplate.fromMessages([
        ["system", qaSystemPrompt],
        new MessagesPlaceholder("chat_history"),
        ["human", "{input}"],
    ]);

    const documentChain = await createStuffDocumentsChain({ llm, prompt: qaPrompt });

    conversationalRetrievalChain = await createRetrievalChain({
        retriever: historyAwareRetrieverChain,
        combineDocsChain: documentChain,
    });

    console.log("Langchain components initialized.");
}

export async function getLegalAssistantResponse(userInput, chatHistory = []) {
    if (!conversationalRetrievalChain) {
        await initializeLangchain();
        if (!conversationalRetrievalChain) {
            throw new Error("Langchain service could not be initialized.");
        }
    }

    console.log("Pinecone API Key:", PINECONE_API_KEY);
    console.log("Pinecone Index Name:", PINECONE_INDEX_NAME);
    console.log("Groq API Key:", GROQ_API_KEY);
    console.log("Hugging Face Token:", HF_TOKEN);


    const formattedHistory = chatHistory.map(msg =>
        msg.role === "user" ? new HumanMessage(msg.content) : new AIMessage(msg.content)
    );

    const result = await conversationalRetrievalChain.invoke({
        chat_history: formattedHistory,
        input: userInput,
    });

    const sources = (result.context || [])
        .map(doc => doc.metadata?.source?.replace(/^data[\\/]/i, '') || null)
        .filter(source => source !== null);

    const uniqueSources = Array.from(new Set(sources));

    return {
        answer: result.answer,
        sources: uniqueSources.length > 0 ? uniqueSources : [],
    };
}
