import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import {
  Search as SearchIcon,
  FileText,
  Sparkles,
  ArrowRight,
  Filter,
  CheckCircle2,
  Calendar,
  Layers
} from 'lucide-react';

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const performSearch = async (searchTerm) => {
    if (!searchTerm.trim()) {
      setResults([]);
      setTotalCount(0);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setHasSearched(true);
    try {
      const res = await api.get(`/search/?q=${encodeURIComponent(searchTerm)}`);
      setResults(res.data.results || []);
      setTotalCount(res.data.count || 0);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery);
    }
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchParams(query ? { q: query } : {});
    performSearch(query);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 md:text-3xl">
          Search Intelligence
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Query across thousands of documents, digital text, OCR rasterizations, and extracted fields.
        </p>
      </div>

      {/* Main Search Input Form */}
      <form onSubmit={handleSearchSubmit} className="relative">
        <div className="flex items-center rounded-3xl border border-white/80 bg-white/90 p-2 shadow-2xl shadow-indigo-500/10 backdrop-blur-xl focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-100 transition-all">
          <SearchIcon className="h-6 w-6 text-indigo-500 ml-3 shrink-0" />
          <input
            type="text"
            placeholder="Search keywords, customer names, dates, amounts, invoice #, terms..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent px-4 py-2.5 text-base text-slate-900 placeholder-slate-400 focus:outline-none"
            autoFocus
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-2.5 text-sm font-bold text-white shadow-md shadow-indigo-500/25 hover:shadow-lg hover:scale-105 active:scale-95 transition-all"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Search results stats */}
      {hasSearched && (
        <div className="flex items-center justify-between text-xs text-slate-500 px-1">
          <span>
            Found <strong className="text-slate-800">{totalCount}</strong> matching documents for{' '}
            <strong className="text-indigo-600">"{query}"</strong>
          </span>
        </div>
      )}

      {/* Results list */}
      <div className="space-y-4">
        {results && results.length > 0 ? (
          results.map((res) => (
            <div
              key={res.id}
              className="rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-indigo-500/5 backdrop-blur-xl hover:border-indigo-300 hover:shadow-2xl hover:scale-[1.01] transition-all duration-300 space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <Link
                  to={`/documents/${res.id}`}
                  className="flex items-center gap-3 group"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 group-hover:scale-105 transition">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition">
                      {res.title}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                      <span className="rounded bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                        {res.category_display}
                      </span>
                      <span>•</span>
                      <span>OCR Quality: {res.ocr_confidence}%</span>
                      <span>•</span>
                      <span>{new Date(res.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </Link>

                <Link
                  to={`/documents/${res.id}`}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 px-4 py-2 text-xs font-bold text-indigo-600 hover:bg-indigo-50 transition shrink-0"
                >
                  <span>Review Document</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              {/* Matched Fields Pills */}
              {res.matched_fields && res.matched_fields.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <span className="text-[11px] font-semibold text-slate-400">Matched Field:</span>
                  {res.matched_fields.map((mf, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1 rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-800"
                    >
                      <span className="text-slate-500">{mf.label}:</span>
                      <strong>{mf.value}</strong>
                    </span>
                  ))}
                </div>
              )}

              {/* Context Text Snippet */}
              {res.snippet && (
                <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-600 font-mono leading-relaxed border border-slate-100">
                  {res.snippet}
                </div>
              )}
            </div>
          ))
        ) : hasSearched && !loading ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center text-slate-400">
            <SearchIcon className="mx-auto h-8 w-8 text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-700">No matching documents found</p>
            <p className="text-xs text-slate-400 mt-1">Try another keyword, date, or customer name.</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

