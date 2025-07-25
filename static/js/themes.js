document.addEventListener('DOMContentLoaded', function() {
  const themeOptions = document.querySelectorAll('.theme-option');
  
  themeOptions.forEach(option => {
    option.style.backgroundColor = option.dataset.bgColor;
    option.style.color = option.dataset.textColor;
    
    option.addEventListener('click', function(e) {
      themeOptions.forEach(opt => opt.classList.remove('active'));
      this.classList.add('active');
    });
  });
});