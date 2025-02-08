"use client"
import { useState } from "react";
import { initialize_crawl } from "../api/search";

export default function SearchForm({ onSearchStarted }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);

    const data = await initialize_crawl(query);
    if (data.search_id) {
      onSearchStarted(data.search_id);  // Pass search_id to parent
    } else {
      alert("Error starting search. Please try again.");
    }

    setLoading(false);
  };


  return (
    <form onSubmit={handleSearch} className="flex items-center">
      <input
        type="text"
        placeholder="Enter business name"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        required
        className="border border-gray-300 text-background p-2 me-0 rounded-l-md w-full h-full"
      />
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-500 hover:bg-blue-600 border border-grey-300 text-foreground p-2 ms-0 rounded-r-md h-full"
      >
        {loading ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
}
