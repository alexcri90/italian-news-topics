/**
 * Visualization script for Italian News Topics
 * Handles rendering of charts and interactive elements
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
  // Function to generate a color palette
  const generateColorPalette = (count) => {
    const baseColors = [
      '#3498db', '#2980b9', '#1abc9c', '#16a085', '#2ecc71', 
      '#27ae60', '#f1c40f', '#f39c12', '#e67e22', '#d35400',
      '#e74c3c', '#c0392b', '#9b59b6', '#8e44ad', '#34495e'
    ];
    
    // If we need more colors than in our base palette, generate more
    if (count <= baseColors.length) {
      return baseColors.slice(0, count);
    }
    
    // Otherwise, generate more colors by rotating hue
    const colors = [...baseColors];
    const neededExtraColors = count - baseColors.length;
    
    for (let i = 0; i < neededExtraColors; i++) {
      // Take a color from our base and modify it slightly
      const baseColor = baseColors[i % baseColors.length];
      // Convert hex to HSL, modify, then back to hex
      const r = parseInt(baseColor.slice(1, 3), 16);
      const g = parseInt(baseColor.slice(3, 5), 16);
      const b = parseInt(baseColor.slice(5, 7), 16);
      
      // Simple color variation
      const newR = (r + 15 * i) % 255;
      const newG = (g + 25 * i) % 255;
      const newB = (b + 35 * i) % 255;
      
      colors.push(`#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`);
    }
    
    return colors;
  };
  
  // Function to render the main entities chart
  const renderEntitiesChart = () => {
    const ctx = document.getElementById('entitiesChart');
    if (!ctx) return; // Guard against missing canvas element
    
    const context = ctx.getContext('2d');
    
    // Get topics data from a global variable (should be set in the template)
    const topicsData = window.topicsData || {
      top_entities: []
    };
    
    // Take top 15 entities
    const entities = topicsData.top_entities.slice(0, 15);
    const labels = entities.map(entity => entity.text);
    const counts = entities.map(entity => entity.count);
    const colors = generateColorPalette(entities.length);
    
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Numero di menzioni',
          data: counts,
          backgroundColor: colors,
          borderColor: colors.map(color => color),
          borderWidth: 1,
          barThickness: 'flex',
          barPercentage: 0.9
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            displayColors: false,
            callbacks: {
              label: (context) => `Menzioni: ${context.raw}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          },
          x: {
            ticks: {
              callback: function(value, index) {
                // Shorten long entity names
                const label = this.getLabelForValue(value);
                return label.length > 15 ? label.substring(0, 12) + '...' : label;
              }
            }
          }
        }
      }
    });
  };
  
  // Function to render source-specific charts
  const renderSourceCharts = () => {
    const topicsData = window.topicsData || {
      top_entities_by_source: {}
    };
    
    // Get source names
    const sources = Object.keys(topicsData.top_entities_by_source);
    
    // Create a chart for each source
    sources.forEach((source, index) => {
      const canvasId = `sourceChart${index + 1}`;
      const canvas = document.getElementById(canvasId);
      
      if (!canvas) return; // Skip if canvas element doesn't exist
      
      const ctx = canvas.getContext('2d');
      
      // Get top 8 entities for this source
      const entities = topicsData.top_entities_by_source[source].slice(0, 8);
      const labels = entities.map(entity => entity.text);
      const counts = entities.map(entity => entity.count);
      const colors = generateColorPalette(entities.length);
      
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: counts,
            backgroundColor: colors,
            borderColor: '#ffffff',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                boxWidth: 15,
                padding: 10,
                font: {
                  size: 11
                }
              }
            },
            tooltip: {
              displayColors: false,
              callbacks: {
                label: (context) => `Menzioni: ${context.raw}`
              }
            }
          },
          cutout: '50%'
        }
      });
    });
  };
  
  // Function to load the topics data from JSON file
  const loadTopicsData = () => {
    fetch('/data/topics.json')
      .then(response => response.json())
      .then(data => {
        // Store data in a global variable for charts to use
        window.topicsData = data;
        
        // Render all charts
        renderEntitiesChart();
        renderSourceCharts();
      })
      .catch(error => {
        console.error('Error loading topics data:', error);
        
        // Display error message on page
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
          container.innerHTML = '<div class="alert alert-danger">Error loading data. Please try again later.</div>';
        });
      });
  };
  
  // If topic data is already included in the page, use it directly
  if (window.topicsData) {
    renderEntitiesChart();
    renderSourceCharts();
  } else {
    // Otherwise, load it from JSON
    loadTopicsData();
  }
  
  // Make keywords in cloud interactive
  const keywordTags = document.querySelectorAll('.keyword-tag');
  keywordTags.forEach(tag => {
    tag.addEventListener('click', () => {
      // Could implement search or filtering functionality here
      console.log(`Keyword clicked: ${tag.textContent.trim()}`);
    });
  });
});