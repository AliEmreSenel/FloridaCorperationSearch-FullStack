const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"


export interface ApiResponse {
  status: string;
  results: Corporation[] | null;
  message: string | null;
}

export interface Corporation {
  id: number;
  type: string;
  principal_addr_changed: string | null;
  mailing_addr_changed: string | null;
  registered_addr: string;
  registered_addr_changed: string | null;
  search_id: number;
  name: string;
  principal_addr: string;
  mailing_addr: string;
  registered_name: string;
  registered_name_changed: string | null;
  officers: Officer[];
  annual_reports: AnnualReport[];
  filing_info: FilingInfo[];
  documents: Document[];
}

export interface Officer {
  title: string;
  id: number;
  address: string;
  name: string;
  corp_id: number;
}

export interface AnnualReport {
  filing_date: string;
  id: number;
  corp_id: number;
  report_year: number;
}

export interface FilingInfo {
  internal_name: string;
  name: string;
  corp_id: number;
  id: number;
  value: string;
}

export interface Document {
  link: string;
  id: number;
  corp_id: number;
  title: string;
}

export async function initialize_crawl(business_name: string) {
  try {
    const response = await fetch(`${API_URL}/search/corporations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: business_name }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Error starting search");
    }
    return data;
  } catch (error: any) {
    throw new Error(error.message || "Network error");
  }
}

export async function get_search_results(search_id: string) {
  try {
    const response = await fetch(`${API_URL}/results/${search_id}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Error retrieving results");
    }

    return data;
  } catch (error: any) {
    throw new Error(error.message || "Network error");
  }
}
