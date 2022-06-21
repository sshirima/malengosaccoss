const passwordToggle1 = document.querySelector('#password1-toggle');
const passwordToggle2 = document.querySelector('#password2-toggle');
const passwordToggle = document.querySelector('#password-toggle');

const password = document.querySelector('#password')
const password1 = document.querySelector('#password1')
const password2 = document.querySelector('#password2')

const passwordIcon = document.querySelector('#password-icon')
const passwordIcon1 = document.querySelector('#password1-icon')
const passwordIcon2 = document.querySelector('#password2-icon')


function onPasswordToggleClick(passwordToggle, passwordField, toggleIcon){

  if(document.body.contains(passwordToggle)){
    passwordToggle.addEventListener('click', (e)=>{
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
  }
  
}

onPasswordToggleClick(passwordToggle, password, passwordIcon)
onPasswordToggleClick(passwordToggle1, password1, passwordIcon1)
onPasswordToggleClick(passwordToggle2, password2, passwordIcon2)