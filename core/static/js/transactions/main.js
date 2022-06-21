
$(document).ready(function() {
  $('.select2').select2();
});

function onChangeMember() {
  const owner = document.querySelector('#owner');
  const loanarea = document.querySelector('#loanarea');
  const owner_id = owner.value;

  if (owner_id.length > 0){
    
    fetch('get-member-loans', {
        body:JSON.stringify({owner_id : owner_id}),
        method:"POST"
    })
    .then(res =>res.json())
    .then(data=>{

        if (data.length === 0){
          loanarea.innerHTML = ''
        } else {

          options = ' <option></option>'

          data.forEach((item) => {
            options +=`
                <option value="${item.id}">${item.type} - ${item.principle}</option>`
          });
          loanarea.innerHTML = `
          <label for="loan" class="col-sm-2 col-form-label">Select Loan </label>
          <div class="col-sm-10" id="loanarea">
            <select name="loan" class="form-control" required > 
              ${options}
            </select>
          </div>  
          `
        }
    })
  } 
  else 
  {
    loanarea.innerHTML = ''
  }
}