// Toggle Dropdown Visibility
const toggleDropdown = (dropdownId) => {
    const dropdown = document.getElementById(dropdownId);
    dropdown.classList.toggle('show');
  };
  
  // Select Affiliation
  const selectAffiliation = (affiliation) => {
    document.getElementById('affiliation-selected').textContent = affiliation;
    closeAllDropdowns();
  };
  
  // Select Major
  const selectMajor = (major) => {
    document.getElementById('major-selected').textContent = major;
    closeAllDropdowns();
  };
  
  // Select SubMajor
  const selectSubMajor = (subMajor) => {
    document.getElementById('submajor-selected').textContent = subMajor;
    closeAllDropdowns();
  };

  // Select available days
  const selectDay = (subDay) => {
    document.getElementById('day-selected').textContent = subDay;
    closeAllDropdowns();
  };

  // Select available hours
  const selectHour = (subHour) => {
    document.getElementById('hour-selected').textContent = subHour;
    closeAllDropdowns();
  };
  
  // Close All Dropdowns
  const closeAllDropdowns = () => {
    document.querySelectorAll('.dropdown-content').forEach((dropdown) => {
      dropdown.classList.remove('show');
    });
  };
  
  // Close dropdowns when clicking outside
  window.onclick = (event) => {
    if (!event.target.matches('.dropbtn')) {
      closeAllDropdowns();
    }
  };
  