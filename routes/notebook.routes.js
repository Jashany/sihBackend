import express from "express";
import {
  addSegment,
  createNotebook,
  deleteNotebook,
  deleteSegment,
  getNotebook,
  updateSegment,
} from "../controllers/notebook.js";
import verifyUser from "../middlewares/verifyUser.js";

const noteBookRouter = express.Router();

noteBookRouter.post("/create-notebook",verifyUser, createNotebook);
noteBookRouter.get("/:id",verifyUser, getNotebook);
noteBookRouter.delete("/:id",verifyUser, deleteNotebook);
noteBookRouter.post("/:id/add-segment",verifyUser, addSegment);
noteBookRouter.post("/:id/update-segment/:segmentId", updateSegment);
noteBookRouter.delete("/:id/delete-segment/:segmentId", verifyUser,deleteSegment);


export default noteBookRouter;
