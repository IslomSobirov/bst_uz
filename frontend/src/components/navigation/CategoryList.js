import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { getApiUrl } from '../../config/api';

function CategoryList({ onCategorySelect, selectedCategory }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollContainerRef = useRef(null);
  const autoScrollIntervalRef = useRef(null);

  const itemsPerPage = 4;

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(getApiUrl('/api/categories/'));
      const categoriesData = response.data.results || response.data || [];
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  // Calculate total items (All + categories)
  const allItems = [{ id: 'all', name: 'All' }, ...categories];
  const totalPages = Math.ceil(allItems.length / itemsPerPage);

  useEffect(() => {
    // Only set up auto-scroll if we have more than 4 items
    if (allItems.length <= itemsPerPage) {
      return;
    }

    // Auto-scroll every 3 seconds
    autoScrollIntervalRef.current = setInterval(() => {
      setCurrentIndex((prevIndex) => {
        const nextIndex = prevIndex < totalPages - 1 ? prevIndex + 1 : 0;
        if (scrollContainerRef.current && scrollContainerRef.current.children.length > 0) {
          const container = scrollContainerRef.current;
          const firstChild = container.children[0];
          const itemWidth = firstChild.offsetWidth;
          const gap = 12;
          const scrollPosition = nextIndex * (itemWidth + gap) * itemsPerPage;
          container.scrollTo({ left: scrollPosition, behavior: 'smooth' });
        }
        return nextIndex;
      });
    }, 3000);

    return () => {
      if (autoScrollIntervalRef.current) {
        clearInterval(autoScrollIntervalRef.current);
      }
    };
  }, [allItems.length, totalPages, itemsPerPage]);

  const scrollToIndex = (index) => {
    if (scrollContainerRef.current && scrollContainerRef.current.children.length > 0) {
      const container = scrollContainerRef.current;
      const firstChild = container.children[0];
      const itemWidth = firstChild.offsetWidth;
      const gap = 12;
      const scrollPosition = index * (itemWidth + gap) * itemsPerPage;
      container.scrollTo({ left: scrollPosition, behavior: 'smooth' });
      setCurrentIndex(index);
    }
  };

  const scrollLeft = () => {
    const newIndex = currentIndex > 0 ? currentIndex - 1 : totalPages - 1;
    scrollToIndex(newIndex);
    // Reset auto-scroll timer
    if (autoScrollIntervalRef.current) {
      clearInterval(autoScrollIntervalRef.current);
    }
    autoScrollIntervalRef.current = setInterval(() => {
      scrollRight();
    }, 3000);
  };

  const scrollRight = () => {
    const newIndex = currentIndex < totalPages - 1 ? currentIndex + 1 : 0;
    scrollToIndex(newIndex);
    // Reset auto-scroll timer
    if (autoScrollIntervalRef.current) {
      clearInterval(autoScrollIntervalRef.current);
    }
    autoScrollIntervalRef.current = setInterval(() => {
      scrollRight();
    }, 3000);
  };

  const handleCategoryClick = (item) => {
    if (item.id === 'all') {
      onCategorySelect && onCategorySelect(null);
    } else {
      onCategorySelect && onCategorySelect(item);
    }
    // Reset auto-scroll timer on manual click
    if (autoScrollIntervalRef.current) {
      clearInterval(autoScrollIntervalRef.current);
    }
    autoScrollIntervalRef.current = setInterval(() => {
      scrollRight();
    }, 3000);
  };

  if (loading) {
    return (
      <div className="w-full h-16 flex items-center justify-center">
        <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (categories.length === 0) {
    return null;
  }

  return (
    <div className="relative w-full max-w-6xl mx-auto mb-8 group">
      <button
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-background/80 backdrop-blur-sm border border-border shadow-md opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-0 hover:bg-accent"
        onClick={scrollLeft}
      >
        <ChevronLeft className="w-5 h-5 text-foreground" />
      </button>

      <div
        className="flex gap-3 overflow-x-auto scrollbar-hide px-12 py-2 snap-x snap-mandatory"
        ref={scrollContainerRef}
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {allItems.map((item) => (
          <button
            key={item.id}
            className={`flex-shrink-0 px-6 py-2.5 rounded-full text-sm font-medium transition-all duration-200 snap-center whitespace-nowrap ${(item.id === 'all' && !selectedCategory) ||
                (selectedCategory && selectedCategory.id === item.id)
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25 scale-105'
                : 'bg-card border border-border/50 text-muted-foreground hover:text-foreground hover:border-primary/30 hover:bg-accent/50'
              }`}
            onClick={() => handleCategoryClick(item)}
          >
            {item.name}
          </button>
        ))}
      </div>

      <button
        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-background/80 backdrop-blur-sm border border-border shadow-md opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-0 hover:bg-accent"
        onClick={scrollRight}
      >
        <ChevronRight className="w-5 h-5 text-foreground" />
      </button>
    </div>
  );
}

export default CategoryList;
