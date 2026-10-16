
/* Simple JS for year and mobile nav toggle */
document.addEventListener('DOMContentLoaded', function(){
  const y = new Date().getFullYear();
  document.getElementById('year')?.textContent = y;
  document.getElementById('year-2')?.textContent = y;
  document.getElementById('year-3')?.textContent = y;
  document.getElementById('year-4')?.textContent = y;

  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');
  if(toggle){
    toggle.addEventListener('click', ()=>{
      if(nav.style.display === 'block'){
        nav.style.display = '';
      } else {
        nav.style.display = 'block';
      }
    });
  }
});
