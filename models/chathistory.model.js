import mongoose from "mongoose";


const AiChatHistory = {
    text : {
        type: String,
        required: true,
    },
    sources : [
        {
            type: String,
        },
    ],
}

const chatHistorySchema = new mongoose.Schema({
    chatId : {
        type: String,
        required: true,
        unique: true,
    },
    ispinned : {
        type: Boolean,
        default: false,
    },
    chatHistory : [
        {
            user : {
                type: String,
                required: true,
            },
            ai : AiChatHistory,
            timestamp : {
                type: Date,
                default: Date.now,
            },
        },
    ],
});
