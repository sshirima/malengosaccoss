
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const passwordField = document.querySelector('.passwordField')
const toggleIcon = document.querySelector('#toggleIcon')

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

// var forms = document.querySelectorAll('.needs-validation')
// // Example starter JavaScript for disabling form submissions if there are invalid fields
// (function () {
//     'use strict'
  
//     // Fetch all the forms we want to apply custom Bootstrap validation styles to
//     var forms = document.querySelectorAll('.needs-validation')
  
//     // Loop over them and prevent submission
//     Array.prototype.slice.call(forms)
//       .forEach(function (form) {
//         form.addEventListener('submit', function (event) {
//           if (!form.checkValidity()) {
//             event.preventDefault()
//             event.stopPropagation()
//           }
  
//           form.classList.add('was-validated')
//         }, false)
//       })
//   })()
  


// const showPasswordToggle = document.querySelector('.showPasswordToggle');
// const passwordField = document.querySelector('#password')

// showPasswordToggle.addEventListener('click', (e)=>{
//     passwordField.setAttribute('type', 'text')
// });