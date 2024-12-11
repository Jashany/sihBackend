import { authUser, forgetpassword, logoutUser, registerUser, resetpassword } from "../controllers/auth.js";
import express from "express";
const authRouter = express.Router();

authRouter.post("/register", registerUser);
authRouter.post("/login", authUser);
authRouter.post("/forgot-password", forgetpassword);
authRouter.post("/reset-password", resetpassword);
authRouter.get("/logout", logoutUser);

export default authRouter;