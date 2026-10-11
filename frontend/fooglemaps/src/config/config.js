import { z } from "zod";

function get_config() {
  const envSchema = z.object({
    GOOGLE_MAPS_API_KEY: z.string(),
    GOOGLE_MAPS_MAP_ID: z.string(),
    GOOGLE_OAUTH_CLIENT_ID: z.string(),
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
    GOOGLE_OAUTH: {
      CLIENT_ID: parsedEnv.data.GOOGLE_OAUTH_CLIENT_ID,
    },
  });
}

const config = get_config();

export default config;
