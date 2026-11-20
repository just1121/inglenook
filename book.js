/*
  Flipbook content. Edit freely.

  - title: shown as the browser tab name and used for the viewer's accessible label.
  - pages: one entry per PDF page, in order.
      alt:        short description of the imagery on the page (read by screen readers).
      transcript: the page's text, one string per paragraph. Visually hidden, read by
                  screen readers. Use [] for pages without text.
      hotspots:   optional clickable areas. left/top/width/height are percentages of the
                  page width and height. label is the accessible name.
  If the PDF gains or loses pages, add or remove entries here to match.
*/
window.FLIPBOOK_BOOK = {
  title: "Inglenook",
  pages: [
    {
      alt: "Cover: the Inglenook chateau and its courtyard fountain, framed by tall trees, with the Inglenook logo.",
      transcript: []
    },
    {
      alt: "Four photographs: a tree-lined drive, the ivy-covered chateau, a pergola with a view of the valley, and three bottles of Inglenook wine on a set table.",
      transcript: [
        "Inglenook lies in the heart of Napa, the world’s most celebrated wine valley. It is a living account of California wine rooted in history, cultivated with patience, and guided by an unwavering commitment to the land. The first vines were planted here in 1879 and since that time, Inglenook has pursued a pure vision: to produce wine of enduring greatness from one of Napa Valley’s most extraordinary estates.",
        "Inglenook holds the rare distinction of being the ninth bonded winery in Napa Valley. For more than a century, the estate has remained true to its founding principles of producing wines of exceptional character from its extraordinary and historic California soil.",
        "Since its founding, Inglenook has passed through the hands of only two remarkable families: the Niebaums, who established the estate’s legacy of excellence, and the Coppolas, who restored and elevated it."
      ]
    },
    {
      alt: "Vintage bottles of Inglenook wine from across the estate's history, arranged on a black background.",
      transcript: []
    },
    {
      alt: "Four photographs: ripening grape clusters, a historic sepia view of the chateau, the chateau lit at night and reflected in the fountain pool, and a bottle of Inglenook Rubicon.",
      transcript: [
        "Inglenook sits at the very center of Rutherford, on the legendary Rutherford Bench. This band of deep, well-drained alluvial soils impart the distinctive dusty richness winemakers call ‘Rutherford Dust.’",
        "Inglenook has continuously made wine on this estate for more than a century, accumulating the deep agricultural knowledge and cellar wisdom that can only be earned through endurance. Each vintage builds upon the last, creating a deep dialogue across generations.",
        "Philippe Bascaules has been at the helm of Inglenook’s winemaking since 2011. He arrived in the Napa Valley with a vision to fuse Inglenook’s storied terroir with contemporary winemaking excellence. Drawing on his esteemed experience at Chateau Margaux, Philippe describes the essence of a great wine as a narrative of the land, crafted into elegance, freshness, and extraordinary longevity."
      ]
    },
    {
      alt: "A long candlelit dinner table with red flowers and black candelabras, set beside rows of barrels in the wine cave.",
      transcript: []
    },
    {
      alt: "Four photographs: two bottles of Inglenook Rubicon with a glass of red wine, a table set for lunch on a veranda overlooking the gardens, an evening dinner under string lights, and a tomato salad.",
      transcript: [
        "The Inglenook Château is one of the great architectural landmarks of American wine country. Built for winemaking in 1887, the stone château has continued to welcome guests for well over a century, immersing them into its history.",
        "We welcome you to wander through the lush vineyards, explore eco-friendly caves, and savor the artistry of wine that tells a story in every glass. Celebrate a special occasion while enjoying the beauty of the sprawling estate, inspired by the courtyards of Paris. Indulge in creations made by Inglenook’s private chef, who pairs Inglenook wines with locally-sourced ingredients that often come from the bounty of the estate’s gardens. The season’s ingredients are turned into memorable meals that bring out the best in each wine.",
        "Enjoy time spent in the company of wines that carry the history of the land and the vision of those who have cared for it. Every vine planted, bottle crafted, and event celebrated at Inglenook adds a new chapter to the family story. It reflects a commitment to fine winemaking and a family legacy that honors the beauty of the land. Please join us in being a part of Inglenook’s tradition.",
        "By appointment · 1991 Saint Helena Highway, PO Box 208, Rutherford, CA 94573 · 707-968-1100 · info@inglenook.com · inglenook.com"
      ],
      hotspots: [
        { href: "tel:+17079681100", label: "Call Inglenook, 707-968-1100",
          left: 62.056, top: 93.889, width: 6.389, height: 2.273 },
        { href: "mailto:info@inglenook.com", label: "Email info@inglenook.com",
          left: 68.986, top: 93.889, width: 8.931, height: 2.273 },
        { href: "https://inglenook.com/", label: "Visit inglenook.com (opens in a new tab)", newTab: true,
          left: 78.472, top: 93.889, width: 6.556, height: 2.273 }
      ]
    },
    {
      alt: "Rows of vines at Inglenook beneath forested hills in warm evening light.",
      transcript: []
    }
  ]
};
