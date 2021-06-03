const box = document.querySelector(".outerbox")
const ontouch = ((e) =>{
    console.log("hello from box")
})

box.addEventListener("click", ontouch)