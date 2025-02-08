"use client"
import { Dispatch, FormEvent, SetStateAction, useState } from "react";
import { initialize_crawl } from "../api/search";

export default function SearchForm({ onSearchStarted, setError, setErrorMessage }: { onSearchStarted: Dispatch<SetStateAction<string>>, setError: Dispatch<SetStateAction<boolean>>, setErrorMessage: Dispatch<SetStateAction<string>> }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = await initialize_crawl(query);
      if (data.search_id) {
        onSearchStarted(data.search_id); // Pass search_id to parent
      } else {
        setError(true);
        setErrorMessage("Error starting search. Please try again.");
      }
    } catch (error: any) {
      setError(true);
      setErrorMessage(error.message);
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
