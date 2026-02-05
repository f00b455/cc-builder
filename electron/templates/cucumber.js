module.exports = {
  default: {
    requireModule: ['ts-node/register'],
    require: ['features/steps/**/*.ts', 'features/support/**/*.ts'],
    format: ['progress', 'html:cucumber-report.html'],
    publishQuiet: true
  }
};
