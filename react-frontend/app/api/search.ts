import axios from "axios";

let API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function initialize_crawl(business_name: string) {
  try {
    let result = await axios.get(`${API_URL}/search/corperation/name/${business_name}`)
    return result.data;
  } catch (error) {
    console.error("Error initializing serch: ", error);
    return { "status": "error", "message": error.message };
  }
}

export async function get_search_results(search_id: string) {
  return axios.get(`${API_URL}/results/${search_id}`)
}
