import mongoose from "mongoose";

const notebookSchema = new mongoose.Schema({
    notebookId: {
        type: String,
        required: true,
        unique: true,
    },
    title: {
        type: String,
        required: true,
    },
    segments : [
        {
            segmentId: {
                type: String,
                required: true,
            },
            notes: {
                type: String,
                required: true,
            },
            document: {
                type: mongoose.Schema.Types.ObjectId,
                ref: "Document",
            },
            created_at: {
                type: Date,
                default: Date.now,
            },
        },
    ],

});

const Notebook = mongoose.model("Notebook", notebookSchema);

export default Notebook;

