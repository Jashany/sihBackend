import express from "express";
import {
  addSegment,
  createNotebook,
  deleteNotebook,
  getNotebook,
  updateSegment,
} from "../controllers/notebook";

const router = express.Router();

router.post("/create-notebook", createNotebook);
router.get("/:id", getNotebook);
router.delete("/:id", deleteNotebook);
router.post("/:id/add-segment", addSegment);
router.post("/:id/update-segment/:segmentId", updateSegment);


export default router;
