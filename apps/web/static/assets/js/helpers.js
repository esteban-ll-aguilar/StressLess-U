function updateCityOptions(countrySelectId, citySelectId, countries) {

  const countrySelect = document.getElementById(countrySelectId);
  const citySelect = document.getElementById(citySelectId);
  
  const selectedCountry = countrySelect.value;

  // Get cities for selected country
  const cities = countries[selectedCountry] || [];

  // Clear existing options
  citySelect.innerHTML = '';

  // Populate new options
  cities.forEach(city => {
      const option = document.createElement('option');
      option.value = city;
      option.textContent = city;
      citySelect.appendChild(option);
  });
}

function hola() {
  alert("holfvfffa") 
}