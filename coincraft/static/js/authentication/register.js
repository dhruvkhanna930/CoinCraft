const usernameField = document.querySelector("#usernameField")
const usernameFeedbackArea = document.querySelector(".usernameFeedbackArea")
const emailField = document.querySelector("#emailField")
const emailFeedbackArea = document.querySelector(".emailFeedbackArea")
const passwordField = document.querySelector("#passwordField")
const showPasswordToggle = document.querySelector(".showPasswordToggle")
const submitButton = document.querySelector("#submit-btn")

handleToggleInput = (e) => {
    console.log("Hello JI")
    if (showPasswordToggle.textContent === "SHOW") {
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", 'text');
    } else {
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", 'password');
    }
}

showPasswordToggle.addEventListener("click", handleToggleInput);


emailField.addEventListener("keyup", (e) => {

    const emailVal = e.target.value
    console.log(emailVal)

    emailField.classList.remove("is-invalid");
    emailFeedbackArea.style.display = "none";

    if (emailVal.length > 0) {


        fetch("/authentication/validate-email/", {
            body: JSON.stringify({ email: emailVal }),
            method: "POST",
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("data", data);
            if (data.email_error) {
                emailField.classList.add("is-invalid");
                emailFeedbackArea.style.display = "block";
                emailFeedbackArea.innerHTML=`<p>${data.email_error}</p>`
                submitButton.disabled = true;
                submitButton.style.opacity = 0.5; 
            } else {
                submitButton.removeAttribute("disabled");
                submitButton.style.opacity = 1;
            }   
          });
    };
});



usernameField.addEventListener("keyup", (e) => {

    const usernameVal = e.target.value
    console.log(usernameVal)

    usernameField.classList.remove("is-invalid");
    usernameFeedbackArea.style.display = "none";

    if (usernameVal.length > 0) {


        fetch("/authentication/validate-username/", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("data", data);
            if (data.username_error) {
                usernameField.classList.add("is-invalid");
                usernameFeedbackArea.style.display = "block";
                submitButton.disabled = true;
                submitButton.style.opacity = 0.5; 
                usernameFeedbackArea.innerHTML=`<p>${data.username_error}</p>`
            } else {
                submitButton.removeAttribute("disabled");
                submitButton.style.opacity = 1;
            }      
          });
    };
});
