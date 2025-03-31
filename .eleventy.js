module.exports = function(eleventyConfig) {
  // Copy static assets to output directory
  eleventyConfig.addPassthroughCopy("assets");
  
  // Copy node_modules files we need
  eleventyConfig.addPassthroughCopy({
    "node_modules/bootstrap/dist/css/bootstrap.min.css": "assets/css/bootstrap.min.css",
    "node_modules/bootstrap/dist/js/bootstrap.bundle.min.js": "assets/js/bootstrap.bundle.min.js",
    "node_modules/chart.js/dist/chart.umd.js": "assets/js/chart.min.js"
  });
  
  // Add date filter for formatting
  eleventyConfig.addFilter("formatDate", function(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("it-IT", {
      year: 'numeric', 
      month: 'long', 
      day: 'numeric'
    });
  });
  
  // Add year filter for copyright
  eleventyConfig.addFilter("year", function() {
    return new Date().getFullYear();
  });
  
  return {
    dir: {
      input: ".",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk", "md", "html"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};