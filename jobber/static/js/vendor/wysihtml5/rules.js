var wysihtml5ParserRules = {
  tags: {

    // check
    a: {
        set_attributes: {
            target: '_blank',
            rel: 'nofollow'
        },
        check_attributes: {
            href: 'url'
        }
    },

    // keep
    abbr: true,
    acronym: true,
    b: true,
    blockquote: true,
    br: true,
    code: true,
    div: true,
    em: true,
    i: true,
    li: true,
    ol: true,
    p: true,
    span: true,
    strong: true,
    ul: true,

    // remove
    script: undefined,
    link: undefined,
    p: undefined
  }
};