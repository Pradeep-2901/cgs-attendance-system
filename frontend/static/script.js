const employeeForm = document.getElementById('employeeForm');
const adminForm = document.getElementById('adminForm');
const toggleBtn = document.getElementById('toggleBtn');

function toggleForms() {
  const isEmployeeVisible = !employeeForm.classList.contains('hidden');

  if (isEmployeeVisible) {
    employeeForm.classList.add('hidden');
    adminForm.classList.remove('hidden');
    toggleBtn.innerText = "Employee";
  } else {
    adminForm.classList.add('hidden');
    employeeForm.classList.remove('hidden');
    toggleBtn.innerText = "Admin";
  }
}

function togglePassword(inputId, iconElement){
    const input = document.getElementById(inputId);
    if (input.type === "password"){
        input.type = "text";
        iconElement.textContent = "🙈";
    }
    else{
        input.type = "password";
        iconElement.textContent = "👁️";
    }
}
