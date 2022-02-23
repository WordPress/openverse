const packageJson = require('./package.json')

function readPackage(pkg, context) {
  if (pkg.dependencies.typescript) {
    pkg.dependencies = {
      ...pkg.dependencies,
      typescript: packageJson.devDependencies.typescript,
    }
    context.log(
      `typescript@${pkg.dependencies.typescript} => typescript@${packageJson.devDependencies.typescript} in dependencies of ${pkg.name}`
    )
  }

  return pkg
}

module.exports = {
  hooks: {
    readPackage,
  },
}
