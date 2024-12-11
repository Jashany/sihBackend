import mongoose from "mongoose";
import fs from "fs";
import path from "path";
import Case from "../models/case.model.js";

const folderPath = "./case_files"; // Path to the folder containing JSON files

// MongoDB connection URL
const dbURL = process.env.MONGO_URL

const seedCases = async () => {
  try {
    // Connect to MongoDB
    await mongoose.connect("mongodb+srv://naman:toggledocs@cluster0.i89bdjl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0/lawvista", {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("Connected to MongoDB");

    // Read files from the folder
    const files = fs.readdirSync(folderPath);
    let index = 1;
    for (const file of files) {
      if (path.extname(file) === ".json") {
        const filePath = path.join(folderPath, file);

        const caseData = JSON.parse(fs.readFileSync(filePath, "utf-8"));

        // Create or update the case in the database
        await Case.updateOne(
          { Case_id: caseData.Case_id }, // Match by Case_id
          { $set: caseData }, // Update data
          { upsert: true } // Insert if it doesn't exist
        );
        console.log(`Seeded: ${file} ${index}`);
        index++;
      }
    }

    console.log("Seeding completed");
    process.exit();
  } catch (error) {
    console.error("Error seeding data:", error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
  }
};

seedCases();
