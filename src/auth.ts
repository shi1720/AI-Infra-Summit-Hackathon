import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
const app = initializeApp({
  projectId: "granted-ai-2026",
  appId: "1:812985487554:web:6a16ac60bcb3e78bfdab5b",
  apiKey: "AIzaSyBmsmI9E6h94rqqgxhwsfNjK26xR984t98",
  authDomain: "granted-ai-2026.firebaseapp.com",
});
export const auth = getAuth(app);
