import dotenv from "dotenv";
import { z } from "zod";

function get_config() {
  const envSchema = z.object({
    GOOGLE_MAPS_API_KEY: z.string(),
    GOOGLE_MAPS_MAP_ID: z.string(),
  });

  const parsedEnv = envSchema.safeParse(import.meta.env);

  if (!parsedEnv.success) {
    console.error(
      "Invalid or missing environment configuration:",
      parsedEnv.error.format(),
    );
  }

  return Object.freeze({
    GOOGLE_MAPS: {
      API_KEY: parsedEnv.data.GOOGLE_MAPS_API_KEY,
      MAP_ID: parsedEnv.data.GOOGLE_MAPS_MAP_ID,
    },
  });
}

const config = get_config();

export default config;
