async def msg_top(ctx, *, args: parser.vtes = parser.vtes.defaults()):
    logger.info("Received instructions %s", ctx.message.content)

    cards = vtes.VTES
    cards.load()

    for k, v in args.items():
        if k == "clan" and v[0] == "!":
            args[k] = v[1:] + " antitribu"
        if k not in {"exclude", "discipline"}:
            for o in cards.search_dimensions[k]:
                if o.lower() == v:
                    v = o
                    args[k] = [o]
        if k == "exclude":
            for o in cards.search_dimensions["type"]:
                if o.lower() == v:
                    v = o
                    args[k] = [o]
        if k == "discipline":
            for o in cards.search_dimensions[k]:
                if o.lower() == v:
                    v = o
                    args[k] = [o]

    exclude_type = args.pop("exclude", None)

    if exclude_type:
        args["type"] = list(
            set(args.get("type", ""))
            | (set(vtes.VTES.search_dimensions["type"]) - set(exclude_type))
        )

    print(args)
    list = cards.search(**args)
    print(list)

    """
	print(args)
	for k,v in args.items():
		if k == "clan" and v[0] == "!":
			v = v[1:] + " antitribu"
		if k not in {"exclude","discipline"}:
			for o in vtes.VTES.search_dimensions[k]:
				if o.lower() == v:
					v = o
					args[k] = [o]
		if k == "exclude":
			for o in vtes.VTES.search_dimensions['type']:
				if o.lower() == v:
					v = o
					args[k] = [o]
		if k == "discipline":
			for o in vtes.VTES.search_dimensions[k]:
				if o.lower() == v:
					v = o
					args[k] = [o]

	exclude_type = args.pop("exclude", None)

	if exclude_type:
		args["type"] = list(
			set(args.get("type", ""))
			| (set(vtes.VTES.search_dimensions['type']) - set(exclude_type))
		)

	print(args)
	_u.filter_vtes(args)
	"""

    """
	vtes.VTES.load()
	logger.info("Received instructions {}", ctx.message.content)
	print(args)
	for k,v in args.items():
		if k == "clan" and v[0] == "!":
			v = v[1:] + " antitribu"
		for o in vtes.VTES.search_dimensions[k]:
			if o.lower() == v:
				v = o
				args[k] = o
		await ctx.send("`[{k}: {v} (type: {t})]` => {r}".format(k=k,v=v,t=type(v),r=(v in vtes.VTES.search_dimensions[k])))
	print(args)
	_u.filter_vtes(args)
	#await ctx.send("I'm sorry dear Metuselah, I'm still working on it, it should be available soon")
	"""
