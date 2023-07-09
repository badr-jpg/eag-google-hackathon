window.onload = function() {
  const getStartedButton = document.getElementById('get-started-button');
  const cards = document.querySelectorAll('.card');
  const nextcard2 = document.getElementById('nextcard2');
  const nextcard1 = document.getElementById('nextcard1');
  const precard1 = document.getElementById('precard1');
  const precard0 = document.getElementById('precard0');
  let currentCard = 0;

  getStartedButton.addEventListener('click', function() {
    document.getElementById('startheader').style.display = "none";
    cards[0].classList.add('active');
  });

  nextcard1.addEventListener('click', function() {
    cards[0].classList.remove('active');
    cards[1].classList.add('active');
  });

  nextcard2.addEventListener('click', function() {
    cards[1].classList.remove('active');
    cards[2].classList.add('active');
  });

  precard1.addEventListener('click', function() {
    cards[2].classList.remove('active');
    cards[1].classList.add('active');
  });

  precard0.addEventListener('click', function() {
    cards[1].classList.remove('active');
    cards[0].classList.add('active');
  });

  

  for (let i = 0; i < cards.length; i++) {
    const form = cards[i].querySelector('form');
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      // Here you can add the code to submit the form and generate the survey
      console.log('Survey generated!');
    });
  }
}
