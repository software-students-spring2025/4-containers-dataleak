category_icons = {
    "Dairy": "🥛",
    "Meat": "🥩",
    "Poultry": "🍗",
    "Seafood": "🐟",
    "Produce": "🥦",
    "Grains & Starch": "🍞",
    "Sweets": "🍰",
    "Snacks": "🍿",
    "Nuts & Legumes": "🌰",
    "Condiments": "🧂",
    "Frozen": "🧊",
    "Other": "📦"
}

CATEGORIES = {
    "Dairy": sorted({
        'blue cheese', 'brie', 'camembert', 'cheddar', 'cottage cheese', 'curd', 'goats cheese', 'gorgonzola', 'gouda', 'grated cheese', 'mozzarella', 'whipped cream', 'yogurt'
    }),
    "Meat": sorted({
        'bacon', 'beef', 'beef carpaccio', 'beef steak', 'blood sausage', 'brisket', 'chorizo', 'corned beef', 'duck', 'filet mignon', 'ground beef', 'ham', 'hamburger', 'lamb', 'lamb chops', 'meat', 'meat pie', 'meatball', 'meatloaf', 'pancetta', 'pastrami', 'pork', 'pork chop', 'prime rib', 'prosciutto', 'roast', 'roast beef', 'salami', 'sausage', 'sausage roll', 'sirloin', 'spare ribs', 'steak', 'tenderloin', 'venison'}),
    "Poultry": sorted({
        'chicken', 'chicken breast', 'chicken curry', 'chicken leg', 'chicken wings', 'deviled eggs', 'drumstick', 'egg', 'egg white', 'egg yolk', 'huevos rancheros', 'omelette', 'turkey', 'turkey breast'}),
    "Seafood": sorted({
        'ceviche', 'clam', 'clam chowder', 'crab', 'crab cakes', 'crayfish', 'cuttlefish', 'eel', 'fillet of sole', 'fish', 'fried calamari', 'halibut', 'herring', 'kingfish', 'kipper', 'lobster', 'lobster bisque', 'lox', 'mackerel', 'mussel', 'octopus', 'oyster', 'perch', 'prawn', 'roe', 'salmon', 'sardine', 'sashimi', 'scallop', 'scampi', 'sea bass', 'seafood', 'shellfish', 'shrimp', 'smoked fish', 'smoked salmon', 'snapper', 'squid', 'sturgeon', 'trout', 'tuna', 'tuna tartare'
    }),
    "Produce": sorted({
        'apple', 'apricot', 'artichoke', 'asparagus', 'avocado', 'basil', 'beet', 'bell pepper', 'berry', 'bibimbap', 'bilberry', 'black currant', 'blackberry', 'blueberry', 'bok choy', 'boysenberry', 'broccoli', 'broccolini', 'caprese salad', 'cauliflower', 'celery', 'chard', 'cherry', 'cherry tomato', 'citrus', 'clementine', 'corn', 'cranberry', 'cress', 'cucumber', 'currant', 'daikon', 'dandelion greens', 'date', 'dragonfruit', 'dried apricot', 'dried fruit', 'eggplant', 'elderberry', 'endive', 'fig', 'florence fennel', 'french beans', 'fruit salad', 'garlic', 'garlic bread', 'garlic chives', 'goji berry', 'gooseberry', 'gourd', 'grape', 'grapefruit', 'green bean', 'green onion', 'guava', 'habanero pepper', 'honeydew melon', 'huckleberry', 'iceberg lettuce', 'jackfruit', 'jalapeno', 'jerusalem artichoke', 'jicama', 'juniper berry', 'kale', 'kiwi fruit', 'kohlrabi', 'kumquat', 'leek', 'lemon', 'lemon peel', 'lentil', 'lettuce', 'lima bean', 'lime', 'lotus root', 'mandarin orange', 'mango', 'melon', 'mint', 'mulberry', 'mushroom', 'napa cabbage', 'nectarine', 'okra', 'onion', 'onion rings', 'orange', 'papaya', 'parsnip', 'passionfruit', 'peach', 'pear', 'plum', 'pomegranate', 'pomelo', 'potato', 'potato onion', 'pumpkin', 'pumpkin seeds', 'quince', 'radicchio', 'radish', 'raspberry', 'rhubarb', 'romaine', 'rosemary', 'rutabaga', 'sage', 'salad', 'scallion', 'seaweed salad', 'shallot', 'snow pea', 'sorrel', 'spinach', 'split peas', 'spring onion', 'sprouts', 'squash', 'squash blossoms', 'star fruit', 'string bean', 'summer squash', 'tomatillo', 'tomato', 'turnip', 'watercress', 'watermelon', 'yam', 'yardlong bean', 'yellow summer squash', 'zucchini'}),
    "Grains & Starch": sorted({
        'amaranth', 'bagel', 'barley', 'biscuits', 'bread', 'bread rolls', 'breadstick', 'brioche', 'brown rice', 'bruschetta', 'buckwheat', 'cereal', 'ciabatta', 'cornbread', 'cornflakes', 'couscous', 'cracker', 'crescent roll', 'crispbread', 'croissant', 'crouton', 'danish pastry', 'doughnut', 'farfalle', 'flatbread', 'focaccia', 'french bread', 'frittata', 'fusilli', 'gnocchi', 'granola', 'grits', 'knish', 'macaroni', 'millet', 'muesli', 'noodle', 'oat', 'oatmeal', 'pasta', 'penne', 'pilaf', 'pita bread', 'polenta', 'quinoa', 'ramen', 'ravioli', 'ribbon-cut pasta', 'rice', 'risotto', 'samosa', 'sandwich', 'scone', 'soda bread', 'spaghetti bolognese', 'spaghetti carbonara', 'spring rolls', 'strudel', 'stuffing', 'toast', 'tortellini', 'vermicelli', 'wafer', 'waffle'
    }),
    "Sweets": sorted({
       'baklava', 'birthday cake', 'bonbon', 'brittle', 'cake', 'cake pop', 'candy', 'candy apple', 'candy bar', 'caramel apple', 'chocolate', 'churros', 'cinnamon roll', 'cookie', 'creme brulee', 'crepe', 'cupcake', 'custard', 'doughnut', 'eclair', 'flan', 'fruitcake', 'fudge', 'galette', 'honey', 'jelly beans', 'macaron', 'macaroon', 'marshmallow', 'marzipan', 'meringue', 'mousse', 'nougat', 'panna cotta', 'parfait', 'pie', 'praline', 'pudding', 'red velvet cake', 'scone', 'sherbet', 'shortcake', 'sorbet', 'sprinkles', 'sundae', 'tiramisu', 'toffee', 'torte', 'whoopie pie'
    }),

    "Snacks": sorted({
        'chips', 'crisps', 'lollipop', 'nacho', 'nachos', 'nougat', 'onion rings', 'popcorn', 'popsicle', 'pretzel', 'salsa', 'tortilla chips'
    }),
    "Nuts & Legumes": sorted({
        'black beans', 'broad beans', 'cashew', 'chickpeas', 'hazelnut', 'sesame seed', 'walnut'
    }),
    "Condiments": sorted({
        'guacamole', 'maple syrup', 'pate', 'pesto', 'pickle'
    }),
    "Frozen": sorted({
        "frozen yogurt", "ice cream"
    }),
    "Other": sorted({
        'antipasto', 'aspic', 'baby back ribs', 'beancurd', 'beans', 'brulee', 'burrito', 'canape', 'caper', 'carp', 'carpaccio', 'casserole', 'ceviche', 'chili', 'chili pepper', 'chowder', 'chutney', 'citron', 'cockle', 'coleslaw', 'common bean', 'compote', 'corn salad', 'croque madame', 'croquette', 'crouton', 'crunch', 'dough', 'dumpling', 'french fries', 'fritter', 'gazpacho', 'gherkin', 'ginger', 'goose', 'goulash', 'gumbo', 'gyoza', 'hash', 'hummus', 'jambalaya', 'kettle corn', 'kidney bean', 'kimchi', 'kombu', 'lavender', 'miso soup', 'mochi', 'muesli', 'olive', 'pad thai', 'paella', 'pierogi', 'pizza', 'polenta', 'popovers', 'poppy seed roll', 'porridge', 'potato', 'potato salad', 'quiche', 'raisin', 'ramen', 'risotto', 'sandwich', 'sashimi', 'sauerbraten', 'savory pie', 'shashlik', "shepherd's pie", 'slaw', 'souffle', 'soup', 'stir-fry', 'succotash', 'sushi', 'taco', 'tapas', 'tartar', 'tartare', 'tempura', 'teriyaki', 'tofu', 'truffle'
    })
}
