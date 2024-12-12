import Chats from "../models/chathistory.model.js";
import axios from "axios";

const MODEL_API = process.env.MODEL_API;

const chatdemo = {
  "message": "Chat found",
  "success": true,
  "data": {
      "_id": "675a37c3bb028b270debe3cd",
      "user": "67598849e330532b239f4a29",
      "chatId": "8826a73a-cd85-4013-af22-1ac23fb4aab7",
      "ispinned": false,
      "chatHistory": [],
      "__v": 0
  }
}

export const getChats = async (req, res) => {
  console.log("hello")
  try {
    const userId = req.user._id;
    console.log("hello")
    const chats = await Chats.find({
      user: userId,
    })

    console.log(chats);

    return res.status(200).json({
      message: "Chats found",
      success: true,
      data: chats,
    })
  } catch (error) {
    console.error("Error getting chats:", error);
    return res.status(500).json({
      message: "Internal Server Error",
      success: false,
    }); 
  }
}

export const createChat = async (req, res) => {
  try {
    const { chatId } = req.body;

    const isChatExist = await Chats.findOne({
      chatId,
    });

    if (isChatExist) {
      return res.status(400).json({
        message: "Chat already exists",
        success: false,
      });
    }

    const chat = await Chats.create({
      chatId,
    });

    if (chat) {
      return res.status(201).json({
        message: "Chat created",
        success: true,
        data: chat,
      });
    } else {
      return res.status(400).json({
        message: "Chat not created",
        success: false,
      });
    }
  } catch (error) {
    return res.status(500).json({
      message: "Internal Server Error",
      success: false,
    });
  }
};

export const getChat = async (req, res) => {
  try {
    const { chatId } = req.params;
    console.log(chatId);

    const chat = await Chats.findOne({
      chatId:chatId,
    });

    if (chat) {
      return res.status(200).json({
        message: "Chat found",
        success: true,
        data: chat,
      });
    } 


    chatdemo.chatId = chatId;

    return res.status(200).json({
      message: "Chat not found",
      success: true,
      data: chatdemo
    });


  } catch (error) {
    console.log(error);
    return res.status(500).json({
      message: "Internal Server Error",
      success: false,
    });
  }
};

export const updateChat = async (req, res) => {
  try {
    const { chatId } = req.params;
    const { userMessage } = req.body;

    // Validate user message
    if (!userMessage) {
      return res.status(400).json({
        message: "User message is required",
        success: false,
      });
    }

    // Find the chat by chatId
    let chat = await Chats.findOne({ chatId });

    if (!chat) {
      chat = await Chats.create({
        chatId,
        user: req.user._id,
      });
    }

    if (req.user._id !== chat.user.toString()) {
      return res.status(401).json({
        message: "Unauthorized",
        success: false,
      });
    }

    const userMsg = {
      user: userMessage,
      ai: undefined,
      timestamp: new Date(),
    };

    chat.chatHistory.push(userMsg);
    await chat.save();

    const aiChatHistory = chat.chatHistory.map((msg) => {
      if (msg.user) {
        return { role: "user", content: msg.user };
      } else if (msg.ai && msg.ai.text) {
        return { role: "assistant", content: msg.ai.text };
      }
      return null;
    }).filter(Boolean);

    let history = aiChatHistory
    console.log(history);

    // Send user message to external AI API
    let aiResponse;
    let source;
    let response;
    try {
      const aiApiResponse = await axios.post(
        "http://127.0.0.1:8000/api/chat/",
        {
          user_input: userMessage,
          chat_history:history,
        }
      );
      response = aiApiResponse.data;
      source = aiApiResponse.data.doc_id
      aiResponse = aiApiResponse.data.assistant_output; // Adjust based on the external API's response structure
    } catch (error) {
      console.error("Error calling external AI API:", error);
      return res.status(500).json({
        message: "Failed to fetch AI response",
        success: false,
        data:chat
      });
    }

    
    

    // Update the chat history
    const newMessage = {
      user: undefined,
      ai: {
        text: aiResponse,
        sources: source
      },
      timestamp: new Date(),
    };

    chat.chatHistory.push(newMessage);
    await chat.save();

    // Return the updated chat
    return res.status(200).json({
      message: "Chat updated",
      success: true,
      data: chat,
      metadata: response
    });
  } catch (error) {
    console.error("Error updating chat:", error);
    return res.status(500).json({
      message: "Internal Server Error",
      success: false,
    });
  }
};

export const deleteChat = async (req, res) => {
  try {
    const { chatId } = req.params;

    const chat = await Chats.findOneAndDelete({
      chatId,
    });

    if (chat) {
      return res.status(200).json({
        message: "Chat deleted",
        success: true,
        data: chat,
      });
    } else {
      return res.status(404).json({
        message: "Chat not found",
        success: false,
      });
    }

  } catch (error) {

  }
}
