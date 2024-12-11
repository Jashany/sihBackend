// Import required modules
import express from 'express';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import caseRouter from './routes/case.routes.js';
import authRouter from './routes/auth.routes.js';
import noteBookRouter from './routes/notebook.routes.js';
import chatRouter from './routes/chat.routes.js';
import docRouter from './routes/doc.routes.js';


dotenv.config();

const app = express();

// Middleware setup
app.use(express.json()); // Parse incoming JSON requests
app.use(cors({ origin: true, credentials: true })); // Enable CORS with credentials
app.use(cookieParser()); // Parse cookies


// Routes
app.use('/api/cases', caseRouter);
app.use("/api/auth", authRouter );
app.use("/api/chat", chatRouter );
app.use("/api/notebook", noteBookRouter );
app.use("/api/doc", docRouter );


// Connect to MongoDB
const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URL, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
        console.log('MongoDB connected');
    } catch (error) {
        console.error('MongoDB connection error:', error.message);
        process.exit(1);
    }
};
connectDB();


// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

