'use strict';

// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";

// Firebase Configuration
const firebaseConfig = {
    apiKey: "",
    authDomain: "",
    projectId: "",
    storageBucket: "",
    messagingSenderId: "",
    appId: ""
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Handle Login
const loginButton = document.getElementById("login");
if (loginButton) {
    loginButton.addEventListener('click', function () {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;
                console.log("Logged in");

                user.getIdToken().then((token) => {
                    document.cookie = "token=" + token + "; path=/; SameSite=Strict";
                    window.location = "/";
                });
            })
            .catch((error) => {
                console.log(error.code + error.message);
                const alertDiv = document.getElementById("alert");
                alertDiv.innerText = "Incorrect email or password. Please try again."; // Show alert
                alertDiv.style.display = "block"; // Display the alert
            });
    });
}

// Handle Signup
const signUpButton = document.getElementById("sign-up");
if (signUpButton) {
    signUpButton.addEventListener('click', function () {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        createUserWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;

                user.getIdToken().then((token) => {
                    document.cookie = "token=" + token + "; path=/; SameSite=Strict";
                    window.location = "/";
                });
            })
            .catch((error) => {
                console.log(error.code + error.message);
            });
    });
}

// Handle Logout
document.addEventListener("DOMContentLoaded", function () {
    const logoutButton = document.getElementById("logout-link");
    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            signOut(auth)
                .then(() => {
                    document.cookie = "token=; path=/; SameSite=Strict";
                    window.location = "/";
                })
                .catch((error) => {
                    console.error("Logout failed:", error);
                });
        });
    }
});
