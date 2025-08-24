'use client';

import { useState, useEffect } from 'react';
import styles from './ExpertSearch.module.css';
import Input from '../ui/Input';
import Button from '../ui/Button';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import SearchIcon from '../icons/SearchIcon';
import FilterIcon from '../icons/FilterIcon';
import UserIcon from '../icons/UserIcon';
import { mockStore } from '../../data/decideaiMockData';
import { formatAvailabilityStatus, formatExperienceYears } from '../../utils/formatters';
import { ExpertProfile, FilterOptions } from '../../types/schema';
import { AvailabilityStatus, Language } from '../../types/enums';

interface ExpertSearchProps {
  onExpertSelect?: (expert: ExpertProfile) => void;
}

export default function ExpertSearch({ onExpertSelect }: ExpertSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filteredExperts, setFilteredExperts] = useState<ExpertProfile[]>(mockStore.experts);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'experience'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const [filters, setFilters] = useState<FilterOptions>({
    skills: [],
    sectors: [],
    regions: [],
    languages: [],
    availability: [],
    experienceMin: 0,
    experienceMax: 20
  });

  const itemsPerPage = 10;

  useEffect(() => {
    let filtered = mockStore.experts.filter(expert => {
      const matchesSearch = !searchQuery || 
        expert.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        expert.sectors.some(sector => sector.toLowerCase().includes(searchQuery.toLowerCase())) ||
        expert.roles.some(role => role.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesAvailability = filters.availability.length === 0 || 
        filters.availability.includes(expert.availability);

      const matchesExperience = expert.yearsExperience >= filters.experienceMin && 
        expert.yearsExperience <= filters.experienceMax;

      const matchesLanguages = filters.languages.length === 0 ||
        filters.languages.some(lang => expert.languages.includes(lang));

      return matchesSearch && matchesAvailability && matchesExperience && matchesLanguages;
    });

    // Sort results
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        case 'rating':
          aValue = a.rating;
          bValue = b.rating;
          break;
        case 'experience':
          aValue = a.yearsExperience;
          bValue = b.yearsExperience;
          break;
        default:
          aValue = a.name;
          bValue = b.name;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredExperts(filtered);
    setCurrentPage(1);
  }, [searchQuery, filters, sortBy, sortOrder]);

  const handleItemSelection = (expertId: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(expertId)) {
      newSelected.delete(expertId);
    } else {
      newSelected.add(expertId);
    }
    setSelectedItems(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedItems.size === filteredExperts.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredExperts.map(expert => expert.id)));
    }
  };

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      skills: [],
      sectors: [],
      regions: [],
      languages: [],
      availability: [],
      experienceMin: 0,
      experienceMax: 20
    });
  };

  const paginatedExperts = filteredExperts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const totalPages = Math.ceil(filteredExperts.length / itemsPerPage);

  const getAvailabilityBadgeVariant = (availability: AvailabilityStatus) => {
    switch (availability) {
      case AvailabilityStatus.AVAILABLE:
        return 'success';
      case AvailabilityStatus.BUSY:
        return 'warning';
      case AvailabilityStatus.UNAVAILABLE:
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <div className={styles.expertSearch}>
      <div className={styles.header}>
        <h1>Find Experts</h1>
        <p>Search and discover experts by skills, sectors, regions, and availability</p>
      </div>

      <div className={styles.searchBar}>
        <Input
          placeholder="Search experts by skills, sectors, or regions..."
          value={searchQuery}
          onChange={setSearchQuery}
          leftIcon={<SearchIcon width={20} height={20} />}
          className={styles.searchInput}
        />
        <Button
          variant={showFilters ? 'primary' : 'secondary'}
          onClick={() => setShowFilters(!showFilters)}
        >
          <FilterIcon width={20} height={20} />
          Filters
        </Button>
      </div>

      {showFilters && (
        <Card className={styles.filterPanel}>
          <div className={styles.filterHeader}>
            <h3>Advanced Filters</h3>
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear All
            </Button>
          </div>
          
          <div className={styles.filterGrid}>
            <div className={styles.filterGroup}>
              <label>Availability</label>
              <div className={styles.checkboxGroup}>
                {Object.values(AvailabilityStatus).map(status => (
                  <label key={status} className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={filters.availability.includes(status)}
                      onChange={(e) => {
                        const newAvailability = e.target.checked
                          ? [...filters.availability, status]
                          : filters.availability.filter(a => a !== status);
                        handleFilterChange('availability', newAvailability);
                      }}
                    />
                    {formatAvailabilityStatus(status)}
                  </label>
                ))}
              </div>
            </div>

            <div className={styles.filterGroup}>
              <label>Languages</label>
              <div className={styles.checkboxGroup}>
                {Object.values(Language).map(language => (
                  <label key={language} className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={filters.languages.includes(language)}
                      onChange={(e) => {
                        const newLanguages = e.target.checked
                          ? [...filters.languages, language]
                          : filters.languages.filter(l => l !== language);
                        handleFilterChange('languages', newLanguages);
                      }}
                    />
                    {language.charAt(0).toUpperCase() + language.slice(1)}
                  </label>
                ))}
              </div>
            </div>

            <div className={styles.filterGroup}>
              <label>Experience Range</label>
              <div className={styles.rangeInputs}>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={filters.experienceMin}
                  onChange={(e) => handleFilterChange('experienceMin', parseInt(e.target.value))}
                  className={styles.rangeInput}
                />
                <span>to</span>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={filters.experienceMax}
                  onChange={(e) => handleFilterChange('experienceMax', parseInt(e.target.value))}
                  className={styles.rangeInput}
                />
                <span>years</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      <div className={styles.resultsHeader}>
        <div className={styles.resultsInfo}>
          <span>{filteredExperts.length} experts found</span>
          {selectedItems.size > 0 && (
            <span className={styles.selectedInfo}>
              {selectedItems.size} selected
            </span>
          )}
        </div>
        
        <div className={styles.controls}>
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field as 'name' | 'rating' | 'experience');
              setSortOrder(order as 'asc' | 'desc');
            }}
            className={styles.sortSelect}
          >
            <option value="name-asc">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
            <option value="rating-desc">Highest Rated</option>
            <option value="rating-asc">Lowest Rated</option>
            <option value="experience-desc">Most Experience</option>
            <option value="experience-asc">Least Experience</option>
          </select>
          
          <Button variant="ghost" size="sm" onClick={handleSelectAll}>
            {selectedItems.size === filteredExperts.length ? 'Deselect All' : 'Select All'}
          </Button>
        </div>
      </div>

      <div className={styles.expertGrid}>
        {paginatedExperts.map(expert => (
          <Card
            key={expert.id}
            variant="outlined"
            className={`${styles.expertCard} ${selectedItems.has(expert.id) ? styles.selected : ''}`}
            onClick={() => onExpertSelect?.(expert)}
          >
            <div className={styles.expertHeader}>
              <div className={styles.expertAvatar}>
                <UserIcon width={24} height={24} />
              </div>
              <div className={styles.expertInfo}>
                <h3>{expert.name}</h3>
                <p>{expert.email}</p>
              </div>
              <input
                type="checkbox"
                checked={selectedItems.has(expert.id)}
                onChange={(e) => {
                  e.stopPropagation();
                  handleItemSelection(expert.id);
                }}
                className={styles.selectCheckbox}
              />
            </div>

            <div className={styles.expertDetails}>
              <div className={styles.expertMeta}>
                <Badge variant={getAvailabilityBadgeVariant(expert.availability)}>
                  {formatAvailabilityStatus(expert.availability)}
                </Badge>
                <span className={styles.experience}>
                  {formatExperienceYears(expert.yearsExperience)}
                </span>
                <span className={styles.rating}>
                  ⭐ {expert.rating}
                </span>
              </div>

              <div className={styles.expertSectors}>
                {expert.sectors.slice(0, 3).map(sector => (
                  <Badge key={sector} variant="default" size="sm">
                    {sector}
                  </Badge>
                ))}
                {expert.sectors.length > 3 && (
                  <Badge variant="default" size="sm">
                    +{expert.sectors.length - 3} more
                  </Badge>
                )}
              </div>

              <div className={styles.expertLanguages}>
                {expert.languages.map(language => (
                  <span key={language} className={styles.language}>
                    {language}
                  </span>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {totalPages > 1 && (
        <div className={styles.pagination}>
          <Button
            variant="ghost"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Previous
          </Button>
          
          <div className={styles.pageNumbers}>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <button
                key={page}
                className={`${styles.pageButton} ${page === currentPage ? styles.active : ''}`}
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </button>
            ))}
          </div>
          
          <Button
            variant="ghost"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}