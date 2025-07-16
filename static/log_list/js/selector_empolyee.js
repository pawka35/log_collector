document.addEventListener('DOMContentLoaded', function() {
  new SlimSelect({
    select: '#id_employee',
    settings: {
      placeholderText: 'Select employee',
    }
  });
});
