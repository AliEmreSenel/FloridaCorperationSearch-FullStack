"use client"
import { useState, useEffect } from 'react';
import SearchForm from './components/search_form';
import { get_search_results } from './api/search';
import ResultsDisplay from './components/results_display';

const POLL_INTERVAL = 1000; // 3 seconds

export default function Home() {
  const [results, setResults] = useState([]);
  const [searchId, setSearchId] = useState("");
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!searchId) return;

    setSearching(true);
    setError(false);

    const interval = setInterval(async () => {
      try {
        const data = await get_search_results(searchId);

        if (data.detail) {
          if (data.detail === "pending") {
            return;
          }
          setError(true);
          setErrorMessage(data.detail);
          setResults([]);
          setSearching(false);
          clearInterval(interval);
        } else if (data.length > 0) {
          setResults(data);
          setSearching(false);
          clearInterval(interval);
        }
      } catch (error: any) {
        setError(true);
        setErrorMessage(error.message);
        setResults([]);
        setSearching(false);
        clearInterval(interval);
      }
    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [searchId]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Florida Business Search</h1>
      <SearchForm onSearchStarted={setSearchId} setErrorMessage={setErrorMessage} setError={setError} />
      {searching && (
        <p className="mt-4 text-blue-500">Searching... Please wait.</p>
      )}
      {error && (
        <p className='mt-4 text-red-500'>Error while searching: {errorMessage}</p>
      )}
      <ResultsDisplay results={results} />
    </div>
  );
}
