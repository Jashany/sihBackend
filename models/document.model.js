import mongoose from "mongoose";

const documentSchema = new mongoose.Schema({
    documentId: {
        type: String,
        required: true,
        unique: true,
    },
    summary: {
        type: String,
        required: true,
    },
    judgement: {
        type: String,
        required: true,
    },
    legal_stature: [
        {
            type: String,
        },
    ],
    releventCases: [
        {
            type: String,
        },
    ],
    created_at: {
        type: Date,
        default: Date.now,
    },
});

const Document = mongoose.model("Document", documentSchema);

export default Document;