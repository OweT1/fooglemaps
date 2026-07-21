## Frontend

A React + Google Maps JavaScript implementation is located in the `src/` directory. To run the frontend locally:

1. Obtain a Google Maps JavaScript API key and Map ID from [Google Cloud Console](https://console.cloud.google.com/google/maps-apis).
2. Configure the environmental variables:
   ```bash
   cp .env.example
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm start
   ```
   The app will be available at `http://localhost:3000` and displays a map of Singapore with markers for popular food centres.

The frontend currently includes:

- Interactive map centered on Singapore
- Markers for notable food centres with info windows showing cuisine types
- Basic responsive layout

Future work will connect this frontend to the API Gateway for dynamic POI search, recommendations, user authentication, and favorites/collections.
