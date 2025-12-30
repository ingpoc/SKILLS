#!/usr/bin/env bash
# SVG Generator for Scroll-Storyteller
# Position-aware, theme-based SVG generation with 25+ element types
#
# Usage:
#   generate_svg_for_chapter <position> <title> <description> <light-var> <dark-var> <fade-class>
#   position: hero|ch1|ch2|ch3|ch4|ch5|finale
#
# Themes detected: biblical, tech, nature, business, growth, historical,
#                  scientific, educational, social, adventure, health,
#                  creative, financial, leadership, abstract

#=============================================================================
# MAIN ENTRY POINT
#=============================================================================

generate_svg_for_chapter() {
  local position="$1"      # hero|ch1|ch2|ch3|finale
  local title="$2"
  local description="$3"
  local light_var="$4"     # e.g., "var(--foam)"
  local dark_var="$5"      # e.g., "var(--deep)"
  local fade_class="${6:-fade-path}"

  local content="${title,,} ${description,,}"  # lowercase
  local theme=$(detect_theme "$content")

  # Generate position-appropriate SVG for detected theme
  case "$position" in
    hero)   generate_hero_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    ch1)    generate_ch1_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    ch2)    generate_ch2_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    ch3)    generate_ch3_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    ch4)    generate_ch4_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    ch5)    generate_ch5_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    finale) generate_finale_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
    *)      generate_ch1_svg "$theme" "$content" "$light_var" "$dark_var" "$fade_class" ;;
  esac
}

#=============================================================================
# THEME DETECTION
#=============================================================================

detect_theme() {
  local content="$1"

  if [[ "$content" =~ (david|goliath|shepherd|faith|prophet|miracle|blessing|redemption|covenant|exodus|parable|biblical|spiritual|god|prayer|angel|heaven|salvation|scripture) ]]; then
    echo "biblical"
  elif [[ "$content" =~ (ai|agent|api|cloud|network|security|platform|data|automation|intelligence|code|software|algorithm|deploy|system|integration|token|encrypt) ]]; then
    echo "tech"
  elif [[ "$content" =~ (nature|tree|forest|ocean|river|mountain|season|growth|ecosystem|climate|plant|animal|earth|garden|flower|leaf|sun|moon|star) ]]; then
    echo "nature"
  elif [[ "$content" =~ (business|enterprise|strategy|team|market|leadership|efficiency|roi|scale|profit|revenue|customer|startup|company|corporate|sales) ]]; then
    echo "business"
  elif [[ "$content" =~ (journey|transformation|learning|challenge|overcome|achieve|evolve|discover|personal|self|identity|hero|quest|growth) ]]; then
    echo "growth"
  elif [[ "$content" =~ (history|revolution|discovery|legacy|founding|era|civilization|monument|heritage|ancient|war|empire|king|queen) ]]; then
    echo "historical"
  elif [[ "$content" =~ (research|experiment|hypothesis|data|breakthrough|innovation|evidence|science|lab|study|theory|discovery|atom|molecule) ]]; then
    echo "scientific"
  elif [[ "$content" =~ (learning|education|knowledge|skills|teaching|student|mastery|curriculum|school|university|lesson|study|book) ]]; then
    echo "educational"
  elif [[ "$content" =~ (community|connection|unity|diversity|belonging|collaboration|social|together|people|group|society|movement|crowd) ]]; then
    echo "social"
  elif [[ "$content" =~ (adventure|quest|exploration|treasure|hero|challenge|map|journey|voyage|expedition|brave|courage) ]]; then
    echo "adventure"
  elif [[ "$content" =~ (health|wellness|healing|balance|strength|recovery|vitality|care|medicine|doctor|heart|body|mind|fitness) ]]; then
    echo "health"
  elif [[ "$content" =~ (creative|artistic|inspiration|design|expression|beauty|craft|vision|art|paint|music|dance|write|create) ]]; then
    echo "creative"
  elif [[ "$content" =~ (financial|investment|wealth|prosperity|planning|returns|money|bank|fund|portfolio|asset|budget|savings) ]]; then
    echo "financial"
  elif [[ "$content" =~ (vision|guidance|empowerment|influence|direction|inspire|lead|mentor|coach|chief|executive|manager) ]]; then
    echo "leadership"
  elif [[ "$content" =~ (time|space|infinity|duality|abstract|concept|philosophy|meaning|eternal|universe|cosmos|existence) ]]; then
    echo "abstract"
  else
    echo "growth"  # Default theme
  fi
}

#=============================================================================
# POSITION-AWARE GENERATORS
#=============================================================================

# HERO: Wide scene (1000x1000), contrast setup
generate_hero_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # Valley scene: small figure left, giant right
      cat <<SVG
        <svg viewBox="0 0 1000 1000" fill="none">
          <!-- Hills background -->
          $(svg_hills "$dark" "0.04" "0 700")
          $(svg_hills "$dark" "0.06" "0 750")
          <!-- Small figure left (David) -->
          <g transform="translate(200, 550) scale(0.8)">
            $(svg_figure_small "$dark" "0.15" "$fade")
          </g>
          <!-- Giant figure right (Goliath) -->
          <g transform="translate(650, 350) scale(1.5)">
            $(svg_figure_large "$light" "0.12" "$fade")
          </g>
          <!-- Divine stars -->
          $(svg_stars "$dark" "0.08" "$fade")
        </svg>
SVG
      ;;
    tech)
      # Network hub with satellites
      cat <<SVG
        <svg viewBox="0 0 1000 1000" fill="none">
          <!-- Satellite nodes -->
          $(svg_network_nodes "$light" "0.06" "$fade" "150 200")
          $(svg_network_nodes "$light" "0.06" "$fade" "800 180")
          $(svg_network_nodes "$light" "0.06" "$fade" "850 700")
          $(svg_network_nodes "$light" "0.06" "$fade" "120 680")
          <!-- Connection flows -->
          $(svg_flow_path "$dark" "0.08" "$fade" "200 250 500 500 800 230")
          $(svg_flow_path "$dark" "0.08" "$fade" "180 650 500 500 820 680")
          <!-- Central hub -->
          <g transform="translate(500, 500)">
            $(svg_hub "$dark" "0.15" "$fade")
          </g>
        </svg>
SVG
      ;;
    nature)
      # Landscape with tree and sun
      cat <<SVG
        <svg viewBox="0 0 1000 1000" fill="none">
          $(svg_sun "$dark" "0.06" "$fade" "800 150")
          $(svg_hills "$dark" "0.05" "0 650")
          $(svg_hills "$dark" "0.07" "0 720")
          <g transform="translate(300, 400) scale(1.5)">
            $(svg_tree "$dark" "0.12" "$fade")
          </g>
          $(svg_path_journey "$dark" "0.08" "$fade" "100 800 500 750 900 780")
        </svg>
SVG
      ;;
    *)
      # Default: Journey/contrast scene
      cat <<SVG
        <svg viewBox="0 0 1000 1000" fill="none">
          $(svg_hills "$dark" "0.05" "0 700")
          $(svg_mountain "$dark" "0.08" "$fade" "700 400")
          <g transform="translate(200, 600) scale(0.9)">
            $(svg_figure_small "$dark" "0.12" "$fade")
          </g>
          $(svg_path_journey "$dark" "0.06" "$fade" "250 750 500 700 750 500")
        </svg>
SVG
      ;;
  esac
}

# CH1: Introduce protagonist (500x500), centered
generate_ch1_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # Shepherd with staff and sheep
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_hills "$dark" "0.06" "0 380")
          $(svg_sun "$dark" "0.05" "$fade" "400 80")
          <!-- Shepherd figure -->
          <g transform="translate(180, 200)">
            $(svg_figure_small "$dark" "0.6" "$fade")
          </g>
          $(svg_staff "$dark" "0.5" "$fade" "280 150")
          <!-- Sheep -->
          $(svg_sheep "$light" "0.3" "$fade" "100 380")
          $(svg_sheep "$light" "0.25" "$fade" "150 400")
          $(svg_sheep "$light" "0.2" "$fade" "350 390")
        </svg>
SVG
      ;;
    tech)
      # Single node with potential
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_grid_bg "$light" "0.03" "$fade")
          <g transform="translate(250, 250)">
            $(svg_hub "$dark" "0.5" "$fade")
          </g>
          <!-- Potential connection hints -->
          $(svg_dotted_circle "$light" "0.15" "$fade" "250 250 150")
          $(svg_dotted_circle "$light" "0.08" "$fade" "250 250 200")
        </svg>
SVG
      ;;
    nature)
      # Seed/sprout
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_soil "$dark" "0.1" "$fade")
          <g transform="translate(250, 300)">
            $(svg_sprout "$dark" "0.5" "$fade")
          </g>
          $(svg_sun "$dark" "0.08" "$fade" "380 80")
        </svg>
SVG
      ;;
    business)
      # Single chess piece or figure
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_grid_bg "$light" "0.02" "$fade")
          <g transform="translate(250, 220)">
            $(svg_figure_small "$dark" "0.5" "$fade")
          </g>
          $(svg_ascending_arrow "$light" "0.15" "$fade" "350 350")
        </svg>
SVG
      ;;
    *)
      # Generic protagonist introduction
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_hills "$dark" "0.05" "0 380")
          <g transform="translate(250, 220)">
            $(svg_figure_small "$dark" "0.5" "$fade")
          </g>
          $(svg_sun "$dark" "0.06" "$fade" "380 80")
        </svg>
SVG
      ;;
  esac
}

# CH2: Imposing obstacle (500x500), fills frame
generate_ch2_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # Giant Goliath with armor
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Ground shadow -->
          $(svg_shadow "$dark" "0.1" "$fade" "250 450 200 30")
          <!-- Giant figure -->
          <g transform="translate(250, 180) scale(1.2)">
            $(svg_figure_large "$light" "0.5" "$fade")
          </g>
          <!-- Spear -->
          $(svg_spear "$light" "0.4" "$fade" "380 50")
          <!-- Shield -->
          $(svg_shield "$light" "0.35" "$fade" "100 250")
        </svg>
SVG
      ;;
    tech)
      # Threat/attack visualization
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Threat arrows incoming -->
          $(svg_threat_arrows "$light" "0.3" "$fade")
          <!-- Vulnerable center -->
          <g transform="translate(250, 250)">
            $(svg_hub "$dark" "0.4" "$fade")
          </g>
          <!-- Warning indicators -->
          $(svg_warning "$light" "0.5" "$fade" "250 120")
        </svg>
SVG
      ;;
    nature)
      # Storm/obstacle
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_storm_clouds "$dark" "0.4" "$fade")
          $(svg_rain "$dark" "0.2" "$fade")
          $(svg_waves "$dark" "0.3" "$fade" "0 400")
        </svg>
SVG
      ;;
    business)
      # Wall/barrier
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_wall "$light" "0.4" "$fade" "250 250")
          <!-- Small figure against wall -->
          <g transform="translate(100, 320) scale(0.6)">
            $(svg_figure_small "$dark" "0.3" "$fade")
          </g>
        </svg>
SVG
      ;;
    *)
      # Generic obstacle
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_mountain "$dark" "0.3" "$fade" "250 150")
          $(svg_shadow "$dark" "0.15" "$fade" "250 450 180 25")
        </svg>
SVG
      ;;
  esac
}

# CH3: Triumph/victory (500x500), radiating energy
generate_ch3_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # David victorious, Goliath fallen
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Radiating light -->
          $(svg_radiate "$dark" "0.06" "$fade" "200 200")
          <!-- Fallen giant mass -->
          $(svg_fallen_mass "$light" "0.2" "$fade" "320 380")
          <!-- Stone trajectory -->
          $(svg_trajectory "$dark" "0.25" "$fade" "120 180 280 320")
          <!-- Triumphant David -->
          <g transform="translate(150, 180)">
            $(svg_figure_triumphant "$dark" "0.7" "$fade")
          </g>
          <!-- Expanding rings -->
          $(svg_rings "$light" "0.06" "$fade" "200 250")
        </svg>
SVG
      ;;
    tech)
      # Protected/secured system
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_radiate "$dark" "0.05" "$fade" "250 250")
          <!-- Shield activated -->
          $(svg_shield_bubble "$dark" "0.3" "$fade" "250 250")
          <!-- Secure hub -->
          <g transform="translate(250, 250)">
            $(svg_hub "$dark" "0.5" "$fade")
          </g>
          <!-- Deflected threats -->
          $(svg_deflected "$light" "0.15" "$fade")
        </svg>
SVG
      ;;
    nature)
      # Full bloom/harvest
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_sun "$dark" "0.1" "$fade" "250 80")
          $(svg_radiate "$dark" "0.04" "$fade" "250 80")
          <g transform="translate(250, 250) scale(1.3)">
            $(svg_tree "$dark" "0.5" "$fade")
          </g>
          $(svg_fruit "$light" "0.4" "$fade")
        </svg>
SVG
      ;;
    *)
      # Generic triumph
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_radiate "$dark" "0.06" "$fade" "250 200")
          <g transform="translate(250, 200)">
            $(svg_figure_triumphant "$dark" "0.6" "$fade")
          </g>
          $(svg_rings "$light" "0.08" "$fade" "250 250")
        </svg>
SVG
      ;;
  esac
}

# CH4: Deepening (500x500), dark bg, escalating tension
# Stakes heighten, obstacles multiply, conflict intensifies
generate_ch4_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # Philistine army assembles, threat multiplies
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Dark clouds gathering -->
          $(svg_clouds "$light" "0.35" "$fade" "80 60")
          $(svg_clouds "$light" "0.3" "$fade" "320 40")
          <!-- Army masses (multiple figures) -->
          <g transform="translate(80, 320)">
            $(svg_figure_large "$light" "0.4" "$fade")
          </g>
          <g transform="translate(180, 340)">
            $(svg_figure_large "$light" "0.35" "$fade")
          </g>
          <g transform="translate(280, 330)">
            $(svg_figure_large "$light" "0.45" "$fade")
          </g>
          <g transform="translate(380, 350)">
            $(svg_figure_large "$light" "0.38" "$fade")
          </g>
          <!-- Spears bristling -->
          $(svg_spears "$light" "0.5" "$fade")
          <!-- Narrowing path -->
          $(svg_path_narrowing "$dark" "0.2" "$fade")
        </svg>
SVG
      ;;
    tech)
      # System under attack, threats converging
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Warning pulses -->
          $(svg_pulse_warning "$light" "0.4" "$fade" "100 100")
          $(svg_pulse_warning "$light" "0.35" "$fade" "400 120")
          $(svg_pulse_warning "$light" "0.45" "$fade" "350 400")
          <!-- Attack vectors -->
          $(svg_attack_vectors "$light" "0.5" "$fade")
          <!-- Stressed hub -->
          <g transform="translate(250, 250)">
            $(svg_hub "$light" "0.6" "$fade")
          </g>
          <!-- Compromised nodes -->
          $(svg_nodes_compromised "$light" "0.4" "$fade")
        </svg>
SVG
      ;;
    nature)
      # Storm intensifies, elements clash
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Storm clouds -->
          $(svg_clouds "$light" "0.5" "$fade" "50 30")
          $(svg_clouds "$light" "0.45" "$fade" "250 20")
          $(svg_clouds "$light" "0.4" "$fade" "400 50")
          <!-- Lightning -->
          $(svg_lightning "$light" "0.6" "$fade" "150 80")
          $(svg_lightning "$light" "0.55" "$fade" "350 60")
          <!-- Bent tree -->
          <g transform="translate(250, 280) rotate(-15)">
            $(svg_tree "$light" "0.5" "$fade")
          </g>
          <!-- Wind lines -->
          $(svg_wind "$light" "0.35" "$fade")
        </svg>
SVG
      ;;
    business)
      # Competition peaks, pressure mounts
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Competitor towers -->
          $(svg_tower "$light" "0.5" "$fade" "80 180")
          $(svg_tower "$light" "0.55" "$fade" "180 150")
          $(svg_tower "$light" "0.45" "$fade" "320 160")
          $(svg_tower "$light" "0.5" "$fade" "420 170")
          <!-- Pressure arrows -->
          $(svg_arrows_converging "$light" "0.4" "$fade" "250 350")
          <!-- Under pressure hub -->
          <g transform="translate(250, 350)">
            $(svg_hub "$light" "0.6" "$fade")
          </g>
        </svg>
SVG
      ;;
    *)
      # Generic intensification
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_clouds "$light" "0.4" "$fade" "100 50")
          $(svg_clouds "$light" "0.35" "$fade" "350 30")
          <!-- Multiple obstacles -->
          $(svg_obstacle "$light" "0.5" "$fade" "120 280")
          $(svg_obstacle "$light" "0.45" "$fade" "250 260")
          $(svg_obstacle "$light" "0.5" "$fade" "380 290")
          <!-- Narrowing path -->
          $(svg_path_narrowing "$dark" "0.25" "$fade")
          <!-- Protagonist facing odds -->
          <g transform="translate(250, 380)">
            $(svg_figure_small "$light" "0.55" "$fade")
          </g>
        </svg>
SVG
      ;;
  esac
}

# CH5: Climax (500x500), light bg, decisive confrontation
# Final showdown, turning point, maximum drama
generate_ch5_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # David's final stand, sling drawn
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Divine light breaks through -->
          $(svg_light_rays "$dark" "0.15" "$fade" "250 80")
          <!-- Stone in motion -->
          $(svg_stone_flying "$dark" "0.8" "$fade" "200 180")
          <!-- David in action -->
          <g transform="translate(120, 280)">
            $(svg_figure_action "$dark" "0.7" "$fade")
          </g>
          <!-- Goliath recoiling -->
          <g transform="translate(350, 200) scale(1.2)">
            $(svg_figure_recoiling "$dark" "0.5" "$fade")
          </g>
          <!-- Impact moment -->
          $(svg_impact "$dark" "0.6" "$fade" "320 200")
        </svg>
SVG
      ;;
    tech)
      # Defense fully activated, counterattack
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Full shield -->
          $(svg_shield_bubble "$dark" "0.4" "$fade" "250 250")
          <!-- Central hub powered -->
          <g transform="translate(250, 250)">
            $(svg_hub "$dark" "0.8" "$fade")
          </g>
          <!-- Countermeasures deployed -->
          $(svg_countermeasures "$dark" "0.5" "$fade")
          <!-- Victory signals -->
          $(svg_pulse_success "$dark" "0.3" "$fade" "250 250")
        </svg>
SVG
      ;;
    nature)
      # Breaking through storm, sunlight pierces
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Parting clouds -->
          $(svg_clouds_parting "$dark" "0.2" "$fade")
          <!-- Sunbeams break through -->
          $(svg_light_rays "$dark" "0.4" "$fade" "250 50")
          $(svg_sun "$dark" "0.3" "$fade" "250 80")
          <!-- Tree standing tall -->
          <g transform="translate(250, 280)">
            $(svg_tree "$dark" "0.7" "$fade")
          </g>
          <!-- New growth -->
          $(svg_sprouts "$dark" "0.5" "$fade")
        </svg>
SVG
      ;;
    business)
      # Strategic victory, breakthrough moment
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          <!-- Victory burst -->
          $(svg_radiate "$dark" "0.15" "$fade" "250 200")
          <!-- Rising above competition -->
          $(svg_tower "$dark" "0.7" "$fade" "250 150")
          <!-- Competitor towers below -->
          $(svg_tower "$dark" "0.25" "$fade" "100 320")
          $(svg_tower "$dark" "0.25" "$fade" "400 340")
          <!-- Success indicators -->
          $(svg_arrows_rising "$dark" "0.5" "$fade")
        </svg>
SVG
      ;;
    *)
      # Generic climax
      cat <<SVG
        <svg viewBox="0 0 500 500" fill="none">
          $(svg_light_rays "$dark" "0.2" "$fade" "250 150")
          <!-- Decisive moment -->
          <g transform="translate(250, 220)">
            $(svg_figure_action "$dark" "0.7" "$fade")
          </g>
          <!-- Obstacle overcome -->
          $(svg_obstacle_shattered "$dark" "0.4" "$fade" "250 350")
          <!-- Victory rings -->
          $(svg_rings "$dark" "0.15" "$fade" "250 250")
        </svg>
SVG
      ;;
  esac
}

# FINALE: Symbolic summary (400x400), iconic
generate_finale_svg() {
  local theme="$1" content="$2" light="$3" dark="$4" fade="$5"

  case "$theme" in
    biblical)
      # Crown of victory with stone symbol
      cat <<SVG
        <svg viewBox="0 0 400 400" fill="none">
          <!-- Light rays -->
          $(svg_light_rays "$dark" "0.08" "$fade" "200 200")
          <!-- Crown -->
          <g transform="translate(200, 180)">
            $(svg_crown "$light" "0.5" "$fade")
          </g>
          <!-- Stone symbol callback -->
          $(svg_stone "$dark" "0.3" "$fade" "200 280")
          <!-- Dove of peace -->
          $(svg_dove "$light" "0.2" "$fade" "280 120")
        </svg>
SVG
      ;;
    tech)
      # Unified network symbol
      cat <<SVG
        <svg viewBox="0 0 400 400" fill="none">
          $(svg_concentric "$light" "0.15" "$fade" "200 200")
          <g transform="translate(200, 200)">
            $(svg_hub "$dark" "0.5" "$fade")
          </g>
          $(svg_orbit_nodes "$dark" "0.25" "$fade" "200 200")
        </svg>
SVG
      ;;
    nature)
      # Tree of life / cycle complete
      cat <<SVG
        <svg viewBox="0 0 400 400" fill="none">
          $(svg_concentric "$dark" "0.06" "$fade" "200 200")
          <g transform="translate(200, 200)">
            $(svg_tree "$dark" "0.4" "$fade")
          </g>
          $(svg_cycle_arrows "$light" "0.15" "$fade" "200 200")
        </svg>
SVG
      ;;
    *)
      # Generic finale: unity symbol
      cat <<SVG
        <svg viewBox="0 0 400 400" fill="none">
          $(svg_concentric "$light" "0.1" "$fade" "200 200")
          $(svg_light_rays "$dark" "0.06" "$fade" "200 200")
          <g transform="translate(200, 200)">
            $(svg_star "$dark" "0.4" "$fade")
          </g>
        </svg>
SVG
      ;;
  esac
}

#=============================================================================
# SVG ELEMENT GENERATORS (25+)
#=============================================================================

# 1. Figure: Small protagonist
svg_figure_small() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="figure-small $fade">
      <!-- Body/robe -->
      <path fill="$fill" opacity="$opacity"
        d="M0 40 Q15 45 22 75 Q25 110 22 145 Q15 165 0 170 Q-15 165 -22 145 Q-25 110 -22 75 Q-15 45 0 40 Z"/>
      <!-- Head -->
      <ellipse cx="0" cy="18" rx="18" ry="20" fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)"/>
      <!-- Arms -->
      <path fill="$fill" opacity="$(echo "$opacity * 0.8" | bc)"
        d="M-20 60 Q-40 65 -55 58 Q-60 52 -55 48 Q-38 45 -18 52 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.8" | bc)"
        d="M20 60 Q40 55 58 65 Q63 70 58 75 Q42 72 22 68 Z"/>
    </g>
SVG
}

# 2. Figure: Large antagonist
svg_figure_large() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="figure-large $fade">
      <!-- Massive torso -->
      <path fill="$fill" opacity="$opacity"
        d="M-80 40 Q-70 0 -30 -20 Q20 -40 70 -20 Q110 0 120 40 Q130 100 120 160 Q110 200 70 210 Q20 220 -30 210 Q-70 200 -80 160 Q-90 100 -80 40 Z"/>
      <!-- Helmet with crest -->
      <path fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)"
        d="M-30 -60 Q-10 -90 20 -95 Q50 -90 70 -60 Q80 -30 70 -10 Q50 5 20 10 Q-10 5 -30 -10 Q-40 -30 -30 -60 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.9" | bc)"
        d="M15 -95 Q20 -120 25 -95 Q30 -70 20 -70 Q10 -70 15 -95 Z"/>
      <!-- Legs -->
      <path fill="$fill" opacity="$(echo "$opacity * 0.7" | bc)"
        d="M-50 180 Q-55 230 -60 280 Q-65 310 -45 315 Q-25 310 -30 280 Q-35 240 -30 200 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.7" | bc)"
        d="M70 180 Q75 230 80 280 Q85 310 105 315 Q125 310 120 280 Q115 240 110 200 Z"/>
    </g>
SVG
}

# 3. Figure: Triumphant pose
svg_figure_triumphant() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="figure-triumphant $fade scale-path">
      <!-- Body -->
      <path fill="$fill" opacity="$opacity"
        d="M0 20 Q15 25 20 55 Q23 90 20 125 Q15 145 0 150 Q-15 145 -20 125 Q-23 90 -20 55 Q-15 25 0 20 Z"/>
      <!-- Head raised -->
      <ellipse cx="0" cy="-5" rx="16" ry="18" fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)"/>
      <!-- Arms raised in V -->
      <path fill="$fill" opacity="$(echo "$opacity * 0.85" | bc)"
        d="M-15 35 Q-30 15 -42 -5 Q-47 -15 -38 -18 Q-25 -12 -10 15 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.85" | bc)"
        d="M15 35 Q30 15 42 -5 Q47 -15 38 -18 Q25 -12 10 15 Z"/>
    </g>
SVG
}

# 4. Hills: Rolling landscape
svg_hills() {
  local fill="$1" opacity="$2" translate="${3:-0 0}"
  local tx=$(echo "$translate" | cut -d' ' -f1)
  local ty=$(echo "$translate" | cut -d' ' -f2)
  cat <<SVG
    <g transform="translate($tx, $ty)">
      <path fill="$fill" opacity="$opacity"
        d="M0 80 Q80 40 160 60 Q240 80 320 50 Q400 20 500 60 L500 200 L0 200 Z"/>
    </g>
SVG
}

# 5. Sun: Radiating light source
svg_sun() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-400 100}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="$fade">
      <circle cx="$cx" cy="$cy" r="45" fill="$fill" opacity="$opacity"/>
      <circle cx="$cx" cy="$cy" r="30" fill="$fill" opacity="$(echo "$opacity * 0.7" | bc)"/>
    </g>
SVG
}

# 6. Tree: Growth/life
svg_tree() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="tree $fade">
      <!-- Trunk -->
      <path fill="$fill" opacity="$opacity"
        d="M-8 80 Q-10 40 -5 0 Q0 -20 5 0 Q10 40 8 80 Z"/>
      <!-- Crown -->
      <path fill="$fill" opacity="$(echo "$opacity * 0.8" | bc)"
        d="M-60 -20 Q-40 -60 0 -70 Q40 -60 60 -20 Q70 20 50 50 Q0 70 -50 50 Q-70 20 -60 -20 Z"/>
    </g>
SVG
}

# 7. Staff: Shepherd's crook
svg_staff() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-280 150}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <path class="staff $fade draw-path" stroke="$fill" stroke-width="4" fill="none" opacity="$opacity"
      d="M$x $(($y + 250)) Q$(($x + 5)) $(($y + 150)) $x $(($y + 50)) Q$(($x - 5)) $y $(($x - 30)) $(($y - 10)) Q$(($x - 50)) $(($y - 15)) $(($x - 40)) $(($y + 5))"/>
SVG
}

# 8. Sheep: Pastoral element
svg_sheep() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-100 380}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="sheep $fade" transform="translate($x, $y)">
      <ellipse cx="0" cy="0" rx="25" ry="18" fill="$fill" opacity="$opacity"/>
      <ellipse cx="-20" cy="-5" rx="10" ry="8" fill="$fill" opacity="$(echo "$opacity * 0.9" | bc)"/>
    </g>
SVG
}

# 9. Crown: Victory symbol
svg_crown() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="crown $fade scale-path">
      <!-- Base band -->
      <path fill="$fill" opacity="$opacity"
        d="M-70 20 Q-60 0 -40 -5 Q0 -10 40 -5 Q60 0 70 20 Q60 35 40 40 Q0 45 -40 40 Q-60 35 -70 20 Z"/>
      <!-- Points -->
      <path fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)" d="M-55 0 Q-45 -30 -35 -5"/>
      <path fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)" d="M-25 -5 Q-15 -45 -5 -10"/>
      <path fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)" d="M0 -10 Q10 -55 20 -10"/>
      <path fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)" d="M25 -5 Q35 -40 45 0"/>
      <path fill="$fill" opacity="$(echo "$opacity * 1.1" | bc)" d="M55 0 Q65 -25 70 5"/>
      <!-- Jewel -->
      <ellipse cx="0" cy="15" rx="10" ry="8" fill="$fill" opacity="$(echo "$opacity * 1.3" | bc)"/>
    </g>
SVG
}

# 10. Shield: Protection
svg_shield() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-100 250}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="shield $fade" transform="translate($x, $y)">
      <ellipse cx="0" cy="0" rx="45" ry="60" fill="$fill" opacity="$opacity"/>
      <ellipse cx="0" cy="0" rx="30" ry="40" fill="$fill" opacity="$(echo "$opacity * 0.5" | bc)"/>
    </g>
SVG
}

# 11. Spear: Weapon
svg_spear() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-380 50}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="spear $fade">
      <path stroke="$fill" stroke-width="6" fill="none" opacity="$opacity"
        d="M$x $(($y + 400)) L$(($x - 20)) $(($y + 200)) L$(($x - 30)) $y"/>
      <path fill="$fill" opacity="$(echo "$opacity * 1.2" | bc)"
        d="M$(($x - 30)) $y Q$(($x - 40)) $(($y - 20)) $(($x - 30)) $(($y - 40)) Q$(($x - 20)) $(($y - 20)) $(($x - 30)) $y Z"/>
    </g>
SVG
}

# 12. Stone: Small power symbol
svg_stone() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-200 280}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <ellipse class="stone $fade scale-path" cx="$x" cy="$y" rx="18" ry="14" fill="$fill" opacity="$opacity"/>
SVG
}

# 13. Radiate: Light burst
svg_radiate() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-250 200}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="radiate $fade" opacity="$opacity">
      <path fill="$fill" d="M$cx $cy L$(($cx - 5)) $(($cy - 150)) L$(($cx + 5)) $(($cy - 150)) Z"/>
      <path fill="$fill" d="M$cx $cy L$(($cx - 100)) $(($cy - 120)) L$(($cx - 90)) $(($cy - 130)) Z"/>
      <path fill="$fill" d="M$cx $cy L$(($cx + 100)) $(($cy - 120)) L$(($cx + 90)) $(($cy - 130)) Z"/>
      <path fill="$fill" d="M$cx $cy L$(($cx + 150)) $(($cy - 50)) L$(($cx + 140)) $(($cy - 60)) Z"/>
      <path fill="$fill" d="M$cx $cy L$(($cx - 150)) $(($cy - 50)) L$(($cx - 140)) $(($cy - 60)) Z"/>
    </g>
SVG
}

# 14. Rings: Expanding circles
svg_rings() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-250 250}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="rings $fade" opacity="$opacity">
      <circle cx="$cx" cy="$cy" r="60" fill="none" stroke="$fill" stroke-width="1"/>
      <circle cx="$cx" cy="$cy" r="100" fill="none" stroke="$fill" stroke-width="1"/>
      <circle cx="$cx" cy="$cy" r="140" fill="none" stroke="$fill" stroke-width="1"/>
      <circle cx="$cx" cy="$cy" r="180" fill="none" stroke="$fill" stroke-width="1"/>
    </g>
SVG
}

# 15. Trajectory: Motion arc
svg_trajectory() {
  local fill="$1" opacity="$2" fade="$3" coords="${4:-120 180 280 320}"
  local x1=$(echo "$coords" | cut -d' ' -f1)
  local y1=$(echo "$coords" | cut -d' ' -f2)
  local x2=$(echo "$coords" | cut -d' ' -f3)
  local y2=$(echo "$coords" | cut -d' ' -f4)
  local mx=$(( (x1 + x2) / 2 ))
  local my=$(( y1 - 60 ))
  cat <<SVG
    <path class="trajectory $fade draw-path" stroke="$fill" stroke-width="2" stroke-dasharray="8 4" fill="none" opacity="$opacity"
      d="M$x1 $y1 Q$mx $my $x2 $y2"/>
SVG
}

# 16. Fallen mass: Defeated antagonist
svg_fallen_mass() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-320 380}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <path class="fallen $fade" fill="$fill" opacity="$opacity"
      d="M$(($x - 80)) $y Q$(($x - 60)) $(($y - 40)) $(($x)) $(($y - 50)) Q$(($x + 60)) $(($y - 40)) $(($x + 100)) $y Q$(($x + 60)) $(($y + 30)) $(($x)) $(($y + 20)) Q$(($x - 60)) $(($y + 30)) $(($x - 80)) $y Z"/>
SVG
}

# 17. Stars: Divine/celestial
svg_stars() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="stars $fade">
      <circle cx="150" cy="120" r="3" fill="$fill" opacity="$opacity"/>
      <circle cx="300" cy="80" r="2" fill="$fill" opacity="$opacity"/>
      <circle cx="500" cy="150" r="3" fill="$fill" opacity="$opacity"/>
      <circle cx="700" cy="100" r="2" fill="$fill" opacity="$opacity"/>
      <circle cx="850" cy="180" r="3" fill="$fill" opacity="$opacity"/>
      <circle cx="400" cy="200" r="2" fill="$fill" opacity="$opacity"/>
    </g>
SVG
}

# 18. Network nodes: Tech element
svg_network_nodes() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-150 200}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="node $fade">
      <circle cx="$x" cy="$y" r="30" fill="$fill" opacity="$opacity"/>
      <circle cx="$x" cy="$y" r="15" fill="$fill" opacity="$(echo "$opacity * 1.5" | bc)"/>
    </g>
SVG
}

# 19. Hub: Central tech element
svg_hub() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="hub $fade scale-path">
      <circle cx="0" cy="0" r="50" fill="$fill" opacity="$opacity"/>
      <circle cx="0" cy="0" r="30" fill="$fill" opacity="$(echo "$opacity * 0.6" | bc)"/>
      <circle cx="0" cy="0" r="12" fill="$fill" opacity="$(echo "$opacity * 1.2" | bc)"/>
    </g>
SVG
}

# 20. Flow path: Connection line
svg_flow_path() {
  local fill="$1" opacity="$2" fade="$3" coords="${4:-200 250 500 500 800 230}"
  local x1=$(echo "$coords" | cut -d' ' -f1)
  local y1=$(echo "$coords" | cut -d' ' -f2)
  local x2=$(echo "$coords" | cut -d' ' -f3)
  local y2=$(echo "$coords" | cut -d' ' -f4)
  local x3=$(echo "$coords" | cut -d' ' -f5)
  local y3=$(echo "$coords" | cut -d' ' -f6)
  cat <<SVG
    <path class="flow $fade draw-path" stroke="$fill" stroke-width="3" fill="none" opacity="$opacity"
      d="M$x1 $y1 Q$x2 $y2 $x3 $y3"/>
SVG
}

# 21. Light rays: Finale element
svg_light_rays() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-200 200}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="rays $fade" opacity="$opacity">
      <path fill="$fill" d="M$cx $(($cy - 30)) L$(($cx - 8)) $(($cy - 120)) L$(($cx + 8)) $(($cy - 120)) Z"/>
      <path fill="$fill" d="M$(($cx + 25)) $(($cy - 15)) L$(($cx + 80)) $(($cy - 90)) L$(($cx + 95)) $(($cy - 80)) Z"/>
      <path fill="$fill" d="M$(($cx - 25)) $(($cy - 15)) L$(($cx - 80)) $(($cy - 90)) L$(($cx - 95)) $(($cy - 80)) Z"/>
      <path fill="$fill" d="M$(($cx + 30)) $cy L$(($cx + 110)) $(($cy - 20)) L$(($cx + 115)) $(($cy - 5)) Z"/>
      <path fill="$fill" d="M$(($cx - 30)) $cy L$(($cx - 110)) $(($cy - 20)) L$(($cx - 115)) $(($cy - 5)) Z"/>
    </g>
SVG
}

# 22. Concentric: Unity symbol
svg_concentric() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-200 200}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="concentric $fade">
      <circle cx="$cx" cy="$cy" r="150" fill="$fill" opacity="$(echo "$opacity * 0.3" | bc)"/>
      <circle cx="$cx" cy="$cy" r="100" fill="$fill" opacity="$(echo "$opacity * 0.5" | bc)"/>
      <circle cx="$cx" cy="$cy" r="50" fill="$fill" opacity="$(echo "$opacity * 0.7" | bc)"/>
    </g>
SVG
}

# 23. Dove: Peace symbol
svg_dove() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-280 120}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="dove $fade" transform="translate($x, $y)">
      <path fill="$fill" opacity="$opacity"
        d="M0 0 Q20 -10 40 0 Q50 10 40 20 Q20 25 0 15 Q-10 10 0 0 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.8" | bc)"
        d="M-5 5 Q-30 -10 -50 5 Q-30 0 -5 10 Z"/>
    </g>
SVG
}

# 24. Shadow: Ground effect
svg_shadow() {
  local fill="$1" opacity="$2" fade="$3" params="${4:-250 450 200 30}"
  local cx=$(echo "$params" | cut -d' ' -f1)
  local cy=$(echo "$params" | cut -d' ' -f2)
  local rx=$(echo "$params" | cut -d' ' -f3)
  local ry=$(echo "$params" | cut -d' ' -f4)
  cat <<SVG
    <ellipse class="shadow $fade" cx="$cx" cy="$cy" rx="$rx" ry="$ry" fill="$fill" opacity="$opacity"/>
SVG
}

# 25. Mountain: Obstacle/goal
svg_mountain() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-250 150}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <path class="mountain $fade" fill="$fill" opacity="$opacity"
      d="M$(($x - 150)) $(($y + 250)) Q$(($x - 100)) $(($y + 150)) $(($x - 50)) $(($y + 50)) Q$(($x)) $y $(($x + 50)) $(($y + 50)) Q$(($x + 100)) $(($y + 150)) $(($x + 150)) $(($y + 250)) Z"/>
SVG
}

# 26. Path journey: Winding road
svg_path_journey() {
  local fill="$1" opacity="$2" fade="$3" coords="${4:-100 800 500 750 900 780}"
  local x1=$(echo "$coords" | cut -d' ' -f1)
  local y1=$(echo "$coords" | cut -d' ' -f2)
  local x2=$(echo "$coords" | cut -d' ' -f3)
  local y2=$(echo "$coords" | cut -d' ' -f4)
  local x3=$(echo "$coords" | cut -d' ' -f5)
  local y3=$(echo "$coords" | cut -d' ' -f6)
  cat <<SVG
    <path class="path-journey $fade draw-path" stroke="$fill" stroke-width="4" fill="none" opacity="$opacity"
      d="M$x1 $y1 Q$x2 $y2 $x3 $y3"/>
SVG
}

# Additional helper elements

svg_grid_bg() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="grid $fade" opacity="$opacity">
      <path stroke="$fill" stroke-width="1" fill="none" d="M0 100 H500 M0 200 H500 M0 300 H500 M0 400 H500"/>
      <path stroke="$fill" stroke-width="1" fill="none" d="M100 0 V500 M200 0 V500 M300 0 V500 M400 0 V500"/>
    </g>
SVG
}

svg_dotted_circle() {
  local fill="$1" opacity="$2" fade="$3" params="${4:-250 250 150}"
  local cx=$(echo "$params" | cut -d' ' -f1)
  local cy=$(echo "$params" | cut -d' ' -f2)
  local r=$(echo "$params" | cut -d' ' -f3)
  cat <<SVG
    <circle class="$fade" cx="$cx" cy="$cy" r="$r" fill="none" stroke="$fill" stroke-width="2" stroke-dasharray="10 5" opacity="$opacity"/>
SVG
}

svg_sprout() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="sprout $fade scale-path">
      <path fill="$fill" opacity="$opacity" d="M0 50 Q-5 25 0 0 Q5 25 0 50 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.8" | bc)" d="M0 20 Q-25 10 -30 -10 Q-20 5 0 15 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.8" | bc)" d="M0 30 Q25 20 35 0 Q20 15 0 25 Z"/>
    </g>
SVG
}

svg_soil() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <path class="soil $fade" fill="$fill" opacity="$opacity"
      d="M0 350 Q50 340 100 350 Q200 360 300 350 Q400 340 500 350 L500 500 L0 500 Z"/>
SVG
}

svg_ascending_arrow() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-350 350}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="arrow $fade" transform="translate($x, $y)">
      <path fill="$fill" opacity="$opacity" d="M0 0 L-20 40 L-8 40 L-8 80 L8 80 L8 40 L20 40 Z"/>
    </g>
SVG
}

svg_wall() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-250 250}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <path class="wall $fade" fill="$fill" opacity="$opacity"
      d="M$(($x - 20)) $(($y - 150)) Q$(($x - 15)) $(($y - 160)) $(($x)) $(($y - 160)) Q$(($x + 15)) $(($y - 160)) $(($x + 20)) $(($y - 150)) L$(($x + 25)) $(($y + 150)) Q$(($x + 20)) $(($y + 160)) $(($x)) $(($y + 160)) Q$(($x - 20)) $(($y + 160)) $(($x - 25)) $(($y + 150)) Z"/>
SVG
}

svg_threat_arrows() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="threats $fade">
      <path fill="$fill" opacity="$opacity" d="M50 50 L80 80 L70 85 L95 110 L65 95 L70 105 L45 75 Z"/>
      <path fill="$fill" opacity="$opacity" d="M450 50 L420 80 L430 85 L405 110 L435 95 L430 105 L455 75 Z"/>
      <path fill="$fill" opacity="$opacity" d="M50 450 L80 420 L70 415 L95 390 L65 405 L70 395 L45 425 Z"/>
      <path fill="$fill" opacity="$opacity" d="M450 450 L420 420 L430 415 L405 390 L435 405 L430 395 L455 425 Z"/>
    </g>
SVG
}

svg_warning() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-250 120}"
  local x=$(echo "$pos" | cut -d' ' -f1)
  local y=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="warning $fade scale-path" transform="translate($x, $y)">
      <path fill="$fill" opacity="$opacity" d="M0 -40 L35 30 L-35 30 Z"/>
      <path fill="$fill" opacity="0.3" d="M0 -20 L0 10"/>
      <circle cx="0" cy="20" r="5" fill="$fill" opacity="0.3"/>
    </g>
SVG
}

svg_storm_clouds() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="clouds $fade">
      <path fill="$fill" opacity="$opacity"
        d="M50 100 Q100 60 180 80 Q250 50 320 90 Q380 70 420 110 Q450 90 480 120 L480 180 Q420 200 320 190 Q200 210 100 180 Q50 170 50 100 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.7" | bc)"
        d="M80 150 Q150 120 250 140 Q350 110 420 150 L420 200 Q350 230 250 210 Q150 240 80 200 Z"/>
    </g>
SVG
}

svg_rain() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="rain $fade">
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M100 200 L90 280"/>
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M150 220 L140 300"/>
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M200 190 L190 270"/>
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M250 210 L240 290"/>
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M300 200 L290 280"/>
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M350 220 L340 300"/>
      <path stroke="$fill" stroke-width="2" opacity="$opacity" d="M400 195 L390 275"/>
    </g>
SVG
}

svg_waves() {
  local fill="$1" opacity="$2" fade="$3" translate="${4:-0 400}"
  local tx=$(echo "$translate" | cut -d' ' -f1)
  local ty=$(echo "$translate" | cut -d' ' -f2)
  cat <<SVG
    <g transform="translate($tx, $ty)" class="waves $fade">
      <path fill="$fill" opacity="$opacity"
        d="M0 30 Q50 10 100 30 Q150 50 200 30 Q250 10 300 30 Q350 50 400 30 Q450 10 500 30 L500 100 L0 100 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.6" | bc)"
        d="M0 50 Q50 30 100 50 Q150 70 200 50 Q250 30 300 50 Q350 70 400 50 Q450 30 500 50 L500 100 L0 100 Z"/>
    </g>
SVG
}

svg_shield_bubble() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-250 250}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="shield-bubble $fade">
      <circle cx="$cx" cy="$cy" r="120" fill="none" stroke="$fill" stroke-width="3" opacity="$opacity"/>
      <circle cx="$cx" cy="$cy" r="100" fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity * 0.5" | bc)"/>
    </g>
SVG
}

svg_deflected() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="deflected $fade">
      <path stroke="$fill" stroke-width="2" stroke-dasharray="5 3" opacity="$opacity" d="M80 150 Q100 180 140 170"/>
      <path stroke="$fill" stroke-width="2" stroke-dasharray="5 3" opacity="$opacity" d="M420 150 Q400 180 360 170"/>
      <path stroke="$fill" stroke-width="2" stroke-dasharray="5 3" opacity="$opacity" d="M80 350 Q100 320 140 330"/>
      <path stroke="$fill" stroke-width="2" stroke-dasharray="5 3" opacity="$opacity" d="M420 350 Q400 320 360 330"/>
    </g>
SVG
}

svg_fruit() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="fruit $fade">
      <circle cx="200" cy="180" r="12" fill="$fill" opacity="$opacity"/>
      <circle cx="280" cy="200" r="10" fill="$fill" opacity="$opacity"/>
      <circle cx="320" cy="160" r="11" fill="$fill" opacity="$opacity"/>
      <circle cx="180" cy="220" r="9" fill="$fill" opacity="$opacity"/>
    </g>
SVG
}

svg_orbit_nodes() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-200 200}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="orbit $fade">
      <circle cx="$(($cx))" cy="$(($cy - 80))" r="12" fill="$fill" opacity="$opacity"/>
      <circle cx="$(($cx + 70))" cy="$(($cy + 40))" r="12" fill="$fill" opacity="$opacity"/>
      <circle cx="$(($cx - 70))" cy="$(($cy + 40))" r="12" fill="$fill" opacity="$opacity"/>
    </g>
SVG
}

svg_cycle_arrows() {
  local fill="$1" opacity="$2" fade="$3" pos="${4:-200 200}"
  local cx=$(echo "$pos" | cut -d' ' -f1)
  local cy=$(echo "$pos" | cut -d' ' -f2)
  cat <<SVG
    <g class="cycle $fade draw-path">
      <path stroke="$fill" stroke-width="3" fill="none" opacity="$opacity"
        d="M$(($cx - 80)) $(($cy - 30)) Q$(($cx - 60)) $(($cy - 80)) $(($cx)) $(($cy - 80)) Q$(($cx + 60)) $(($cy - 80)) $(($cx + 80)) $(($cy - 30))"/>
      <path stroke="$fill" stroke-width="3" fill="none" opacity="$opacity"
        d="M$(($cx + 80)) $(($cy + 30)) Q$(($cx + 60)) $(($cy + 80)) $(($cx)) $(($cy + 80)) Q$(($cx - 60)) $(($cy + 80)) $(($cx - 80)) $(($cy + 30))"/>
    </g>
SVG
}

svg_star() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="star $fade scale-path">
      <path fill="$fill" opacity="$opacity"
        d="M0 -50 L12 -15 L50 -15 L20 10 L30 50 L0 25 L-30 50 L-20 10 L-50 -15 L-12 -15 Z"/>
    </g>
SVG
}

#=============================================================================
# CH4/CH5 SPECIALIZED ELEMENTS
#=============================================================================

svg_clouds() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="cloud $fade">
      <path fill="$fill" opacity="$opacity"
        d="M0 50 Q20 20 50 30 Q80 10 120 25 Q150 15 180 35 Q200 55 180 70 Q150 85 100 75 Q50 80 20 70 Q-10 60 0 50 Z"/>
    </g>
SVG
}

svg_spears() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="spears $fade">
      <path fill="$fill" opacity="$opacity" d="M100 0 L105 80 L100 90 L95 80 Z" transform="rotate(5)"/>
      <path fill="$fill" opacity="$(echo "$opacity - 0.05" | bc)" d="M150 10 L155 90 L150 100 L145 90 Z" transform="rotate(-3)"/>
      <path fill="$fill" opacity="$(echo "$opacity + 0.05" | bc)" d="M200 5 L205 85 L200 95 L195 85 Z" transform="rotate(8)"/>
      <path fill="$fill" opacity="$opacity" d="M250 15 L255 95 L250 105 L245 95 Z" transform="rotate(-5)"/>
      <path fill="$fill" opacity="$(echo "$opacity - 0.08" | bc)" d="M300 0 L305 80 L300 90 L295 80 Z" transform="rotate(2)"/>
    </g>
SVG
}

svg_path_narrowing() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="path-narrowing $fade">
      <path fill="$fill" opacity="$opacity"
        d="M0 500 Q100 480 200 420 Q250 380 250 350 Q250 380 300 420 Q400 480 500 500 L500 500 L0 500 Z"/>
    </g>
SVG
}

svg_pulse_warning() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="pulse-warning $fade">
      <circle fill="none" stroke="$fill" stroke-width="2" opacity="$opacity" r="30"/>
      <circle fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity * 0.7" | bc)" r="45"/>
      <circle fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity * 0.4" | bc)" r="60"/>
      <circle fill="$fill" opacity="$opacity" r="8"/>
    </g>
SVG
}

svg_attack_vectors() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="attack-vectors $fade">
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M50 50 L180 180"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M450 50 L320 180"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M50 450 L180 320"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M450 450 L320 320"/>
      <polygon fill="$fill" opacity="$opacity" points="180,180 160,175 165,160"/>
      <polygon fill="$fill" opacity="$opacity" points="320,180 340,175 335,160"/>
      <polygon fill="$fill" opacity="$opacity" points="180,320 160,325 165,340"/>
      <polygon fill="$fill" opacity="$opacity" points="320,320 340,325 335,340"/>
    </g>
SVG
}

svg_nodes_compromised() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="nodes-compromised $fade">
      <circle fill="$fill" opacity="$opacity" cx="100" cy="100" r="15"/>
      <line stroke="$fill" opacity="$opacity" x1="85" y1="85" x2="115" y2="115" stroke-width="3"/>
      <line stroke="$fill" opacity="$opacity" x1="115" y1="85" x2="85" y2="115" stroke-width="3"/>
      <circle fill="$fill" opacity="$opacity" cx="400" cy="400" r="15"/>
      <line stroke="$fill" opacity="$opacity" x1="385" y1="385" x2="415" y2="415" stroke-width="3"/>
      <line stroke="$fill" opacity="$opacity" x1="415" y1="385" x2="385" y2="415" stroke-width="3"/>
    </g>
SVG
}

svg_lightning() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="lightning $fade">
      <path fill="$fill" opacity="$opacity"
        d="M30 0 L10 60 L25 60 L0 120 L50 50 L35 50 L60 0 Z"/>
    </g>
SVG
}

svg_wind() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="wind $fade">
      <path fill="none" stroke="$fill" stroke-width="2" opacity="$opacity" d="M0 200 Q100 180 200 200 Q300 220 400 200"/>
      <path fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity + 0.1" | bc)" d="M50 240 Q150 220 250 240 Q350 260 450 240"/>
      <path fill="none" stroke="$fill" stroke-width="2" opacity="$opacity" d="M0 280 Q100 260 200 280 Q300 300 400 280"/>
    </g>
SVG
}

svg_tower() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="tower $fade">
      <path fill="$fill" opacity="$opacity"
        d="M0 120 L10 0 L20 0 L25 30 L35 30 L40 0 L50 0 L60 120 Z"/>
    </g>
SVG
}

svg_arrows_converging() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="arrows-converging $fade">
      <polygon fill="$fill" opacity="$opacity" points="0,0 15,-30 0,-15" transform="rotate(-45)"/>
      <polygon fill="$fill" opacity="$opacity" points="0,0 15,-30 0,-15" transform="rotate(45)"/>
      <polygon fill="$fill" opacity="$opacity" points="0,0 15,-30 0,-15" transform="rotate(135)"/>
      <polygon fill="$fill" opacity="$opacity" points="0,0 15,-30 0,-15" transform="rotate(-135)"/>
    </g>
SVG
}

svg_obstacle() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="obstacle $fade">
      <path fill="$fill" opacity="$opacity"
        d="M0 60 Q20 0 40 30 Q60 60 80 20 Q100 40 100 60 L0 60 Z"/>
    </g>
SVG
}

svg_stone_flying() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="stone-flying $fade">
      <ellipse fill="$fill" opacity="$opacity" rx="15" ry="12"/>
      <!-- Motion trail -->
      <path fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity * 0.5" | bc)" d="M-20 5 Q-40 0 -60 5"/>
      <path fill="none" stroke="$fill" stroke-width="1" opacity="$(echo "$opacity * 0.3" | bc)" d="M-25 -5 Q-50 -8 -70 -3"/>
    </g>
SVG
}

svg_figure_action() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="figure-action $fade">
      <circle fill="$fill" opacity="$opacity" r="20"/>
      <path fill="$fill" opacity="$opacity" d="M0 20 Q-5 50 -15 80 L-25 70 L-5 50 L5 50 L25 70 L15 80 Q5 50 0 20"/>
      <!-- Extended arm with sling -->
      <path fill="$fill" opacity="$opacity" d="M0 30 Q20 20 50 10"/>
      <path fill="none" stroke="$fill" stroke-width="2" opacity="$opacity" d="M50 10 Q70 -10 60 -30"/>
    </g>
SVG
}

svg_figure_recoiling() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="figure-recoiling $fade">
      <circle fill="$fill" opacity="$opacity" r="30"/>
      <path fill="$fill" opacity="$opacity" d="M0 30 Q20 70 30 120 L50 100 L20 60 L-20 60 L-50 100 L-30 120 Q-20 70 0 30"/>
      <!-- Arms thrown back -->
      <path fill="$fill" opacity="$opacity" d="M-15 40 Q-50 30 -70 50"/>
      <path fill="$fill" opacity="$opacity" d="M15 40 Q50 30 70 50"/>
    </g>
SVG
}

svg_impact() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="impact $fade">
      <circle fill="$fill" opacity="$opacity" r="20"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.6" | bc)" d="M0 -30 L5 -45 L-5 -45 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.6" | bc)" d="M30 0 L45 5 L45 -5 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.6" | bc)" d="M0 30 L5 45 L-5 45 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.6" | bc)" d="M-30 0 L-45 5 L-45 -5 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.4" | bc)" d="M21 -21 L35 -35 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.4" | bc)" d="M21 21 L35 35 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.4" | bc)" d="M-21 21 L-35 35 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity * 0.4" | bc)" d="M-21 -21 L-35 -35 Z"/>
    </g>
SVG
}

svg_countermeasures() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="countermeasures $fade">
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M250 150 L250 50"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M350 250 L450 250"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M250 350 L250 450"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M150 250 L50 250"/>
      <polygon fill="$fill" opacity="$opacity" points="250,50 240,70 260,70"/>
      <polygon fill="$fill" opacity="$opacity" points="450,250 430,240 430,260"/>
      <polygon fill="$fill" opacity="$opacity" points="250,450 240,430 260,430"/>
      <polygon fill="$fill" opacity="$opacity" points="50,250 70,240 70,260"/>
    </g>
SVG
}

svg_pulse_success() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="pulse-success $fade scale-path">
      <circle fill="none" stroke="$fill" stroke-width="2" opacity="$opacity" r="80"/>
      <circle fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity * 0.7" | bc)" r="110"/>
      <circle fill="none" stroke="$fill" stroke-width="2" opacity="$(echo "$opacity * 0.4" | bc)" r="140"/>
    </g>
SVG
}

svg_clouds_parting() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="clouds-parting $fade">
      <!-- Left clouds receding -->
      <path fill="$fill" opacity="$opacity"
        d="M0 30 Q30 10 60 25 Q90 5 100 30 Q80 50 40 45 Q10 50 0 30 Z"/>
      <path fill="$fill" opacity="$(echo "$opacity + 0.05" | bc)"
        d="M20 80 Q50 60 80 75 Q100 60 120 80 Q100 100 60 95 Q30 100 20 80 Z"/>
      <!-- Right clouds receding -->
      <path fill="$fill" opacity="$opacity"
        d="M400 30 Q430 10 460 25 Q490 5 500 30 Q480 50 440 45 Q410 50 400 30 Z" transform="translate(0,0)"/>
      <path fill="$fill" opacity="$(echo "$opacity + 0.05" | bc)"
        d="M380 80 Q410 60 440 75 Q460 60 480 80 Q460 100 420 95 Q390 100 380 80 Z"/>
    </g>
SVG
}

svg_sprouts() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="sprouts $fade">
      <path fill="$fill" opacity="$opacity" d="M100 450 Q105 420 100 400 Q115 410 120 400 Q115 420 120 450"/>
      <path fill="$fill" opacity="$(echo "$opacity - 0.1" | bc)" d="M200 460 Q205 440 200 420 Q215 430 220 420 Q215 440 220 460"/>
      <path fill="$fill" opacity="$opacity" d="M300 455 Q305 425 300 405 Q315 415 320 405 Q315 425 320 455"/>
      <path fill="$fill" opacity="$(echo "$opacity + 0.1" | bc)" d="M400 450 Q405 420 400 400 Q415 410 420 400 Q415 420 420 450"/>
    </g>
SVG
}

svg_arrows_rising() {
  local fill="$1" opacity="$2" fade="$3"
  cat <<SVG
    <g class="arrows-rising $fade">
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M150 400 L150 300"/>
      <polygon fill="$fill" opacity="$opacity" points="150,300 140,320 160,320"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$opacity" d="M350 420 L350 320"/>
      <polygon fill="$fill" opacity="$opacity" points="350,320 340,340 360,340"/>
      <path fill="none" stroke="$fill" stroke-width="3" opacity="$(echo "$opacity + 0.2" | bc)" d="M250 380 L250 250"/>
      <polygon fill="$fill" opacity="$(echo "$opacity + 0.2" | bc)" points="250,250 240,270 260,270"/>
    </g>
SVG
}

svg_obstacle_shattered() {
  local fill="$1" opacity="$2" fade="$3" pos="$4"
  local x="${pos% *}" y="${pos#* }"
  cat <<SVG
    <g transform="translate($x, $y)" class="obstacle-shattered $fade">
      <!-- Broken pieces scattered -->
      <path fill="$fill" opacity="$opacity" d="M-60 20 L-40 0 L-30 25 Z" transform="rotate(-20)"/>
      <path fill="$fill" opacity="$(echo "$opacity - 0.1" | bc)" d="M-20 30 L0 5 L20 30 Z"/>
      <path fill="$fill" opacity="$opacity" d="M30 25 L50 0 L60 20 Z" transform="rotate(15)"/>
      <path fill="$fill" opacity="$(echo "$opacity - 0.15" | bc)" d="M-10 -20 L5 -40 L20 -15 Z" transform="rotate(10)"/>
    </g>
SVG
}

#=============================================================================
# LEGACY COMPATIBILITY (original 7 functions)
#=============================================================================

generate_identity_svg() { generate_ch1_svg "tech" "" "$1" "$2" "$3"; }
generate_network_svg() { generate_hero_svg "tech" "" "$1" "$2" "$3"; }
generate_protection_svg() { generate_ch2_svg "tech" "" "$1" "$2" "$3"; }
generate_growth_svg() { generate_ch1_svg "nature" "" "$1" "$2" "$3"; }
generate_gateway_svg() { generate_ch2_svg "business" "" "$1" "$2" "$3"; }
generate_trust_svg() { generate_ch3_svg "social" "" "$1" "$2" "$3"; }
generate_unity_svg() { generate_finale_svg "abstract" "" "$1" "$2" "$3"; }
