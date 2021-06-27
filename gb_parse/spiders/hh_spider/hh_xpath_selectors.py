VACANCY = {
    "selector": "//a[@data-qa='vacancy-serp__vacancy-title']/@href",
    "callback": "vacancy_parse",
}

PAGINATION = {
    "selector": "//a[@data-qa='pager-page']/@href",
    "callback": "parse",
}

VACANCY_DATA = {
    "title": {"xpath": "//h1[@data-qa='vacancy-title']/text()"},
    "salary": {"xpath": "//p[@class='vacancy-salary']/span/text()"},
    "description": {"xpath": "//div[@data-qa='vacancy-description']//text()"},
    "skills": {"xpath": "//div[contains(@data-qa, 'skills-element')]/span/text()"},
    "author": {"xpath": "//a[@data-qa='vacancy-company-name']/@href"},
}

COMPANY_DATA = {
    # "company_name": "//span[@data-qa='company-header-title-name']/text()",
    "company_name": "//div[@class='company-header']//h1/span[@data-qa='company-header-title-name']/text()",
    "company_site_link": "//a[@data-qa='sidebar-company-site']/@href",
    "business_spheres": "//div[contains(text(), 'Сферы деятельности')]/../p//text()",
    "description": "//div[@class='g-user-content']/p/text()",
}
