<template>
  <b-container fluid>
    <h3>About</h3>
    <p>AutoDetours is an application allowing the usage of multiples windows toolkit to analyse malware.<br>
      For the moment only PESieve and Detours are integrated.</p>
<p>
PESieve job goal is to unpack a Windows PE malware.<br>
Detours job goal is to unpack a Windows PE malware.</p>
<p>
In one hand, this application could be used as an analysis pipeline for windows malware.<br>
In other hand, it could be used to generate a large dataset which can contains results from differents tools. This dataset could then be used in machine learning to try to classify samples by families.<br>
If you have any questions you can contact us by mail or open an issue/PR on github.<br>
  </p>
    <br>
    <p>This project has been developed by:</p>
    <b-row class="mb-4">
      <ul>
        <li>
          <a href="https://github.com/Kn0wl3dge">Kn0wl3dge</a>
        </li>
        <li>
          <a href="https://github.com/Radion94200">Radion</a>
        </li>
        <li>
          <a href="https://github.com/Prolintos">Prolintos</a>
        </li>
        <li>
          <a href="https://github.com/Deacllock">Deacllock</a>
        </li>
        <li>
          <a href="https://github.com/alexandrefresnais">Alexandre Fresnais</a>
        </li>
        <li>
          <a href="https://github.com/Ewael">Ewaël</a>
        </li>
      </ul>
    </b-row>
    <p>Special thanks to <a href="https://github.com/sebdraven">Sebdraven</a> who supervised us.</p>
  </b-container>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style scoped>
</style>
