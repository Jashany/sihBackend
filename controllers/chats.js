import Chats from "../models/chathistory.model";
import axios from "axios";
import extractInfo from "../utils/extractinfo";

const MODEL_API = process.env.MODEL_API;

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

    const chat = await Chats.findOne({
      chatId,
    });

    if (chat) {
      return res.status(200).json({
        message: "Chat found",
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
    const chat = await Chats.findOne({ chatId });

    if (!chat) {
      return res.status(404).json({
        message: "Chat not found",
        success: false,
      });
    }

    if (req.user._id !== chat.user.toString()) {
      return res.status(401).json({
        message: "Unauthorized",
        success: false,
      });
    }

    // Send user message to external AI API
    let aiResponse;
    try {
      const aiApiResponse = await axios.post(
        MODEL_API,
        {
          message: userMessage,
        }
      );
      aiResponse = aiApiResponse.data.message; // Adjust based on the external API's response structure
    } catch (error) {
      console.error("Error calling external AI API:", error);
      return res.status(500).json({
        message: "Failed to fetch AI response",
        success: false,
      });
    }

    // Update the chat history
    const newMessage = {
      user: userMessage,
      ai: {
        text: aiResponse,
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
    });
  } catch (error) {
    console.error("Error updating chat:", error);
    return res.status(500).json({
      message: "Internal Server Error",
      success: false,
    });
  }
};
