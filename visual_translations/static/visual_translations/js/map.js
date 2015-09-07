var originalWidth = 1000, originalHeight = 750,
            horizontalOffset, verticalOffset;

        var zoom, offset,
            zoomLevel = VT.zoomLevel;
        if(zoomLevel === "large") {
            zoom = 5;
            offset = 2;
            horizontalOffset = originalWidth * offset;
            verticalOffset = originalHeight * offset;
        } else {
            zoom = 1;
            offset = 0;
            horizontalOffset = (window.innerWidth - originalWidth) / 2;
            verticalOffset = (window.innerHeight - originalHeight) / 2;
        }
        d3.select("body").attr("class", zoomLevel);

        var width = originalWidth * zoom,
            height = originalHeight * zoom;

        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("id", "map");

        if(zoomLevel !== "large") {
            svg.style("left", horizontalOffset+"px");
            svg.style("top", verticalOffset+"px");
        }

        d3.json(VT.topoJSONFile, function(error, eu) {
            if (error) return console.error(error);

            var subunits = topojson.feature(eu, eu.objects.subunits);

            // Create a unit projection.
            var projection = d3.geo.mercator()
                .scale(1)
                .translate([0, 0]);

            var path = d3.geo.path()
                .projection(projection);

            // Compute the bounds of a feature of interest, then derive scale & translate.
            var b = path.bounds(subunits),
                s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
                t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

            // Update the projection to use computed scale & translate.
            projection
                .scale(s)
                .translate(t);

            svg.selectAll(".subunit")
                .data(subunits.features)
                .enter()
                .append("path")
                .attr("class", function(d) { return "subunit " + d.id; })

                .attr("d", path);

            svg.append("path")
                .datum(topojson.mesh(eu, eu.objects.subunits, function(a, b) { return a !== b && a.id !== "ENG" && a.id !== "BCR"; }))
                .attr("d", path)
                .attr("class", "subunit-boundary");

            svg.append("path")
                .datum(topojson.mesh(eu, eu.objects.subunits, function(a, b) { return a === b; }))
                .attr("d", path)
                .attr("class", "outer-boundary");
        });

        window.scrollTo(horizontalOffset, verticalOffset);