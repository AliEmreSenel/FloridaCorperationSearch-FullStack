"use client"
import { useState, useEffect } from 'react';
import SearchForm from './components/search_form';
import ResultsTable from './components/results_table';
import { get_search_results } from './api/search';

const POLL_INTERVAL = 1000; // 3 seconds

export default function Home() {
  const [results, setResults] = useState([]);
  const [searchId, setSearchId] = useState(null);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!searchId) return;

    setSearching(true);
    setError(false);
    const interval = setInterval(async () => {
      await get_search_results(searchId).then(res => res.data).then(data => {
        if (data.status == "error") {
          setSearching(false);
          setError(true);
          setResults([]);
          if (data.message) {
            setErrorMessage(data.message);
          } else {
            setErrorMessage("Unknown error occured");
          }
          clearInterval(interval);
        } else if (data.status == "pending") {

        } else if (data.results && data.results.length > 0) {
          setResults(data.results);
          setSearching(false);
          clearInterval(interval);
        }
      }).catch(err => {
        setSearching(false);
        setError(true);
        setErrorMessage(err.message);
        setResults([]);
        clearInterval(interval)
      })

    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [searchId]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Florida Business Search</h1>
      <SearchForm onSearchStarted={setSearchId} />
      {searching && (
        <p className="mt-4 text-blue-500">Searching... Please wait.</p>
      )}
      {error && (
        <p className='mt-4 text-red-500'>Error while searching: {errorMessage}</p>
      )}
      <ResultsTable results={results} />
    </div>
  );
}
