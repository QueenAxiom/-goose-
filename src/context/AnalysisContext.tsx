import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface Analysis {
  id: string;
  company_name: string;
  ipo_date: string;
  ipo_trade_score: number;
  buffett_score: number;
  summary: string;
  timestamp: number;
  pinned?: boolean;
}

interface AnalysisContextType {
  analyses: Analysis[];
  watchlist: Analysis[];
  addAnalysis: (analysis: Omit<Analysis, 'id' | 'timestamp'>) => void;
  removeAnalysis: (id: string) => void;
  addToWatchlist: (analysis: Analysis) => void;
  removeFromWatchlist: (id: string) => void;
  togglePin: (id: string) => void;
  clearHistory: () => void;
}

export const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [watchlist, setWatchlist] = useState<Analysis[]>([]);

  // Load data from AsyncStorage on mount
  useEffect(() => {
    loadData();
  }, []);

  // Save analyses to AsyncStorage
  useEffect(() => {
    saveAnalyses();
  }, [analyses]);

  // Save watchlist to AsyncStorage
  useEffect(() => {
    saveWatchlist();
  }, [watchlist]);

  const loadData = async () => {
    try {
      const [analysesData, watchlistData] = await Promise.all([
        AsyncStorage.getItem('axiom_analyses'),
        AsyncStorage.getItem('axiom_watchlist'),
      ]);

      if (analysesData) {
        setAnalyses(JSON.parse(analysesData));
      }
      if (watchlistData) {
        setWatchlist(JSON.parse(watchlistData));
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const saveAnalyses = async () => {
    try {
      await AsyncStorage.setItem('axiom_analyses', JSON.stringify(analyses));
    } catch (error) {
      console.error('Error saving analyses:', error);
    }
  };

  const saveWatchlist = async () => {
    try {
      await AsyncStorage.setItem('axiom_watchlist', JSON.stringify(watchlist));
    } catch (error) {
      console.error('Error saving watchlist:', error);
    }
  };

  const addAnalysis = (analysis: Omit<Analysis, 'id' | 'timestamp'>) => {
    const newAnalysis: Analysis = {
      ...analysis,
      id: Date.now().toString(),
      timestamp: Date.now(),
    };
    setAnalyses([newAnalysis, ...analyses]);
  };

  const removeAnalysis = (id: string) => {
    setAnalyses(analyses.filter(a => a.id !== id));
  };

  const addToWatchlist = (analysis: Analysis) => {
    if (!watchlist.find(w => w.company_name === analysis.company_name)) {
      setWatchlist([...watchlist, analysis]);
    }
  };

  const removeFromWatchlist = (id: string) => {
    setWatchlist(watchlist.filter(w => w.id !== id));
  };

  const togglePin = (id: string) => {
    setAnalyses(analyses.map(a =>
      a.id === id ? { ...a, pinned: !a.pinned } : a
    ));
  };

  const clearHistory = async () => {
    setAnalyses([]);
    await AsyncStorage.removeItem('axiom_analyses');
  };

  return (
    <AnalysisContext.Provider
      value={{
        analyses,
        watchlist,
        addAnalysis,
        removeAnalysis,
        addToWatchlist,
        removeFromWatchlist,
        togglePin,
        clearHistory,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => {
  const context = React.useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysis must be used within AnalysisProvider');
  }
  return context;
};
