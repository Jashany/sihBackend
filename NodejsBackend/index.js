// Import required modules
import express from 'express';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import caseRouter from './routes/case.routes.js';


dotenv.config();

const app = express();

// Middleware setup
app.use(express.json()); // Parse incoming JSON requests
app.use(cors({ origin: "*", credentials: true })); // Enable CORS with credentials
app.use(cookieParser()); // Parse cookies


// Routes
app.use('/api/cases', caseRouter);

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

