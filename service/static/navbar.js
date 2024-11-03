function toggleDropdown(){
    let dropdown = document.getElementById("accountDropdown");
    if(dropdown.hidden === false){
        dropdown.hidden = true;
    }else{
        dropdown.hidden = false;
    }
}

function toggleMobileNavbar(){
    let closeButton = document.getElementById("closeButton");
    let openButton = document.getElementById("openButton");
    let mobileNavbar = document.getElementById("mobile-menu");
    if(mobileNavbar.hidden === false){
        openButton.classList.remove("hidden");
        openButton.classList.add("block");
        closeButton.classList.add("hidden");
        closeButton.classList.remove("block");
        mobileNavbar.hidden = true;
    }else{
        openButton.classList.add("hidden");
        openButton.classList.remove("block");
        closeButton.classList.remove("hidden");
        closeButton.classList.add("block");
        mobileNavbar.hidden = false;
    }
}