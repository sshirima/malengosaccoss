const showPasswordToggle = document.querySelector('.showPasswordToggle');
const passwordField = document.querySelector('.passwordField')
const toggleIcon = document.querySelector('.toggleIcon')

showPasswordToggle.addEventListener('click', (e)=>{
  if (passwordField.type === 'password'){
    passwordField.setAttribute('type', 'text')
    toggleIcon.classList.remove('fa-eye')
    toggleIcon.classList.add('fa-eye-slash')
  } else {
    passwordField.setAttribute('type', 'password')
    toggleIcon.classList.remove('fa-eye-slash')
    toggleIcon.classList.add('fa-eye')
  }
  
});