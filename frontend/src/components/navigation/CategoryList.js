import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { getApiUrl } from '../config/api';
import './CategoryList.css';

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
      <div className="category-list-container">
        <div className="category-list-loading">Loading categories...</div>
      </div>
    );
  }

  if (categories.length === 0) {
    return null;
  }

  return (
    <div className="category-list-container">
      <button className="carousel-button carousel-button-left" onClick={scrollLeft}>
        ‹
      </button>
      <div className="category-list-scroll" ref={scrollContainerRef}>
        {allItems.map((item) => (
          <button
            key={item.id}
            className={`category-item ${
              (item.id === 'all' && !selectedCategory) ||
              (selectedCategory && selectedCategory.id === item.id)
                ? 'active'
                : ''
            }`}
            onClick={() => handleCategoryClick(item)}
          >
            {item.name}
          </button>
        ))}
      </div>
      <button className="carousel-button carousel-button-right" onClick={scrollRight}>
        ›
      </button>
    </div>
  );
}

export default CategoryList;
