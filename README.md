# 👨‍💻 José Luiz  

**`Desenvolvedor Front-end`**

Me chamo José Luiz, tenho 18 anos e sou natural de Piracaia-SP. Sempre tive afinidade com computadores desde pequeno, o que despertou meu interesse pela área de tecnologia. Assim que concluí o ensino médio, iniciei a graduação em **Análise e Desenvolvimento de Sistemas**.  
Paralelamente, venho me dedicando a cursos por fora para aprofundar meus conhecimentos e evoluir constantemente na área.  

---

### 🌎 Conecte-se comigo  

<p align="left">
    <a href="https://youtube.com/@zzin9096?sub_confirmation=1" target="_blank">
        <img alt="YouTube" title="Inscreva-se no meu canal" src="https://custom-icon-badges.demolab.com/youtube/channel/subscribers/UCCWx2NV1J1SrCu-Fl_gPaZg?color=%23E05D44&label=YouTube&logo=video&logoColor=white&style=for-the-badge&labelColor=CE4630"/>
    </a>
    <a href="https://youtube.com/@zzin9096" target="_blank">
        <img alt="YouTube Views" title="Visualizações no YouTube" src="https://custom-icon-badges.demolab.com/youtube/channel/views/UCCWx2NV1J1SrCu-Fl_gPaZg?color=%23E1AD0E&logo=eye&logoColor=white&style=for-the-badge&labelColor=C79600"/>
    </a>
    <a href="https://github.com/zzin742?tab=followers" target="_blank">
        <img alt="GitHub Followers" title="Me siga no GitHub" src="https://custom-icon-badges.demolab.com/github/followers/zzin742?color=236ad3&labelColor=1155ba&style=for-the-badge&logo=github&label=Seguidores&logoColor=white"/>
    </a>
</p>

---

### ⚡ Tecnologias que uso  

<p>
  <img alt="HTML" title="HTML" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg"/>
  <img alt="CSS" title="CSS" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg"/>
  <img alt="JavaScript" title="JavaScript" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg"/>
  <img alt="React" title="React" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg"/>
  <img alt="Tailwind" title="Tailwind" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg"/>
  <img alt="Git" title="Git" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg"/>
  <img alt="Python" title="Python" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"/>
</p>  

---

### 📊 Estatísticas  

<p align="center">
  <img alt="GitHub Stats" height="200" src="https://github-readme-stats.vercel.app/api?username=zzin742&show_icons=true&theme=tokyonight&include_all_commits=true&locale=pt-br"/>
  <img alt="Top Languages" height="200" src="https://github-readme-stats.vercel.app/api/top-langs/?username=zzin742&theme=tokyonight&layout=compact&custom_title=Tecnologias&langs_count=9"/>
</p>

---

### 🐍 Snake Game  

name: generate animation

on:
  # run automatically every 24 hours
  schedule:
    - cron: "0 */24 * * *" 
  
  # allows to manually run the job at any time
  workflow_dispatch:
  
  # run on every push on the master branch
  push:
    branches:
    - main
    
  

jobs:
  generate:
    permissions: 
      contents: write
    runs-on: ubuntu-latest
    timeout-minutes: 5
    
    steps:
      # generates a snake game from a github user (<github_user_name>) contributions graph, output a svg animation at <svg_out_path>
      - name: generate github-contribution-grid-snake.svg
        uses: Platane/snk/svg-only@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-contribution-grid-snake.svg
            dist/github-contribution-grid-snake-dark.svg?palette=github-dark
          
          
      # push the content of <build_dir> to a branch
      # the content will be available at https://raw.githubusercontent.com/<github_user>/<repository>/<target_branch>/<file> , or as github page
      - name: push github-contribution-grid-snake.svg to the output branch
        uses: crazy-max/ghaction-github-pages@v3.1.0
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
